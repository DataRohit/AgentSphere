# Third-party imports
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
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
    UserReactivationConfirmErrorResponseSerializer,
    UserReactivationConfirmSerializer,
    UserReactivationConfirmSuccessResponseSerializer,
    UserReactivationForbiddenResponseSerializer,
    UserReactivationRequestErrorResponseSerializer,
    UserReactivationRequestSerializer,
    UserReactivationRequestSuccessResponseSerializer,
)

# Get the user model
User = get_user_model()


# User reactivation request view
class UserReactivationRequestView(APIView):
    """User reactivation request view.

    This view handles requests to reactivate a deactivated user account.
    It sends a reactivation email with a link to the specified email address.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        authentication_classes (list): The authentication classes for the view.
        object_label (str): The object label for the response.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Define the permission classes - allow any user
    permission_classes = [AllowAny]

    # No authentication required for this view
    authentication_classes = []

    # Define the object label
    object_label = "user"

    # Define the schema for POST method
    @extend_schema(
        tags=["Users"],
        summary="Request account reactivation.",
        description="""
        Requests reactivation of a deactivated user account.
        Sends a reactivation email with a link to the specified email address.
        """,
        operation_id="users_reactivation_request_create",
        request=UserReactivationRequestSerializer,
        responses={
            status.HTTP_200_OK: UserReactivationRequestSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: UserReactivationRequestErrorResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        """Handle POST request for account reactivation.

        This method processes requests to reactivate a deactivated user account.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Create serializer instance with request data
        serializer = UserReactivationRequestSerializer(data=request.data)

        # Validate the serializer
        if not serializer.is_valid():
            # Return validation errors
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the email from validated data
        email = serializer.validated_data["email"]

        # Get the user by email
        user = User.objects.get(email=email)

        # Generate activation token and uid
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Store the activation token in the database
        with transaction.atomic():
            # Update or create the activation token
            UserActivationToken.objects.update_or_create(
                user=user,
                defaults={"uid": uid, "token": token},
            )

        # Get scheme and domain from settings
        scheme = settings.ACTIVATION_SCHEME
        domain_part = settings.ACTIVATION_DOMAIN

        # Construct full reactivation URL
        relative_reactivation_path = reverse(
            "users:user-reactivation-confirm",
            kwargs={"uid": uid, "token": token},
        )
        reactivation_url = f"{scheme}://{domain_part}{relative_reactivation_path}"

        # Prepare email context
        context = {
            "user": user,
            "reactivation_link": reactivation_url,
            "current_year": timezone.now().year,
            "domain_part": domain_part,
        }

        # Send reactivation email
        send_templated_mail(
            template_name="users/user_reactivation.html",
            subject="Reactivate Your Account",
            context=context,
            recipient_list=[user.email],
        )

        # Return success response
        return Response(
            {
                "message": "Reactivation email sent successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


class UserReactivationConfirmView(APIView):
    """User reactivation confirm view.

    This view handles the confirmation of account reactivation.
    It verifies the activation token and reactivates the account with a new password.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        authentication_classes (list): The authentication classes for the view.
        object_label (str): The object label for the response.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Define the permission classes - allow any user
    permission_classes = [AllowAny]

    # No authentication required for this view
    authentication_classes = []

    # Define the object label
    object_label = "user"

    # Define the schema for POST method
    @extend_schema(
        tags=["Users"],
        summary="Confirm account reactivation.",
        description="""
        Confirms reactivation of a user account using the UID and token from the reactivation link.
        Requires setting a new password.
        """,
        operation_id="users_reactivation_confirm_create",
        request=UserReactivationConfirmSerializer,
        responses={
            status.HTTP_200_OK: UserReactivationConfirmSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: UserReactivationConfirmErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: UserReactivationForbiddenResponseSerializer,
        },
    )
    def post(self, request: Request, uid: str, token: str) -> Response:
        """Handle POST request for confirming account reactivation.

        This method confirms reactivation of a user account and sets a new password.

        Args:
            request (Request): The HTTP request object.
            uid (str): The base64-encoded user ID.
            token (str): The reactivation token.

        Returns:
            Response: The HTTP response object.
        """

        # Create serializer instance with request data
        serializer = UserReactivationConfirmSerializer(
            data=request.data,
            context={"uid": uid, "token": token},
        )

        # Validate the serializer
        if not serializer.is_valid():
            # Return validation errors
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the user from the serializer
        user = serializer.user

        # Get the new password from validated data
        new_password = serializer.validated_data["new_password"]

        # Use transaction.atomic to ensure both operations complete together
        with transaction.atomic():
            # Set the new password
            user.set_password(new_password)

            # Reactivate the account
            user.is_active = True

            # Save the user
            user.save(update_fields=["password", "is_active"])

            # Delete the activation token
            UserActivationToken.objects.filter(user=user).delete()

        # Get domain part for the email footer from settings
        domain_part = settings.ACTIVATION_DOMAIN

        # Prepare reactivation success email context
        context = {
            "user": user,
            "current_year": timezone.now().year,
            "domain_part": domain_part,
        }

        # Send reactivation success email
        send_templated_mail(
            template_name="users/user_reactivation_success.html",
            subject="Account Reactivated Successfully",
            context=context,
            recipient_list=[user.email],
        )

        # Return success response
        return Response(
            {
                "message": "Account reactivated successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )
