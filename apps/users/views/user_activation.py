# Third-party imports
from django.conf import settings
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# Project imports
from apps.common.renderers import GenericJSONRenderer
from apps.common.utils import send_templated_mail
from apps.users.models import UserActivationToken
from apps.users.serializers import (
    UserActivationForbiddenResponseSerializer,
    UserActivationSuccessResponseSerializer,
)


# User activation view
class UserActivationView(APIView):
    """User activation view.

    This view allows users to activate their accounts using the activation link sent to their email.
    The view verifies the token in the database and activates the account if valid.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Disable authentication checks for this view
    authentication_classes = []

    # Define the permission classes
    permission_classes = [AllowAny]

    # Define the object label
    object_label = "activation"

    # Define the schema
    @extend_schema(
        tags=["Users"],
        summary="Activate a user account.",
        description="""
        Activates a user account using the UID and token from the activation link.
        The UID identifies the user, and the token verifies the activation request.
        The activation link is valid for 30 minutes and can only be used once.
        """,
        responses={
            status.HTTP_200_OK: UserActivationSuccessResponseSerializer,
            status.HTTP_403_FORBIDDEN: UserActivationForbiddenResponseSerializer,
        },
    )
    def get(self, request: Request, uid: str, token: str) -> Response:
        """Activate a user account.

        This view allows users to activate their accounts using the activation link sent to their email.
        The activation link is valid for 30 minutes and can only be used once.

        Args:
            request (Request): The HTTP request object.
            uid (str): The base64-encoded user ID.
            token (str): The activation token.

        Returns:
            Response: The HTTP response object.
        """

        try:
            try:
                # Get the activation token from the database with a single query that includes user data
                activation_token = get_object_or_404(
                    UserActivationToken.objects.select_related("user"),
                    uid=uid,
                    token=token,
                )

            except Http404:
                # Return 403 Forbidden with an error message
                return Response(
                    {"error": "Invalid or already used activation link"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Check if the token has expired
            if activation_token.is_expired:
                # Delete the expired token and return error response in a single transaction
                activation_token.delete()

                # Return 403 Forbidden with error message
                return Response(
                    {"error": "Activation link has expired"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Get the user associated with the token (already loaded with select_related)
            user = activation_token.user

            # Prepare flag for atomic update
            user.is_active = True

            # Use transaction.atomic to ensure both operations complete together
            with transaction.atomic():
                # Save the user
                user.save(update_fields=["is_active"])

                # Delete the token since it's been used
                activation_token.delete()

            # Get domain part for the email footer from settings
            domain_part = settings.ACTIVATION_DOMAIN

            # Prepare activation success email context
            context = {
                "user": user,
                "current_year": timezone.now().year,
                "domain_part": domain_part,
            }

            # Send activation success email using utility function
            send_templated_mail(
                template_name="users/user_activation_success.html",
                subject="Account Activated Successfully",
                context=context,
                recipient_list=[user.email],
            )

            # Return success response
            return Response(
                {"message": "Account activated successfully"},
                status=status.HTTP_200_OK,
            )

        except (TypeError, ValueError, AttributeError):
            # Return error response for specific exceptions
            return Response(
                {"error": "Invalid activation link"},
                status=status.HTTP_403_FORBIDDEN,
            )
