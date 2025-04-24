# Third-party imports
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError

# Local application imports
from apps.common.renderers import GenericJSONRenderer
from apps.common.utils import send_templated_mail
from apps.users.models import UserDeletionToken
from apps.users.serializers import (
    UserDeletionConfirmSuccessResponseSerializer,
    UserDeletionForbiddenResponseSerializer,
    UserDeletionRequestSuccessResponseSerializer,
    UserDeletionRequestUnauthorizedResponseSerializer,
)

# Get the user model
User = get_user_model()


# User deletion request view
class UserDeletionRequestView(APIView):
    """User deletion request view.

    This view handles requests to delete a user account.
    It sends a deletion confirmation email with a link to the user.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        object_label (str): The object label for the response.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Define the permission classes - require authentication
    permission_classes = [IsAuthenticated]

    # Define the object label
    object_label = "user"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the user deletion request view.

        This method handles exceptions for the user deletion request view.

        Args:
            exc (Exception): The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # For authentication errors, extract the detail message without nested formatting
        if isinstance(exc, (AuthenticationFailed, TokenError)):
            # Try to extract the detail message if it's a dict
            if hasattr(exc, "detail"):
                # Try to extract the detail message if it's a dict
                if isinstance(exc.detail, dict) and "detail" in exc.detail:
                    # Extract the detail message
                    error_message = str(exc.detail["detail"])
                else:
                    # Extract the detail message
                    error_message = str(exc.detail)
            else:
                # Extract the detail message
                error_message = str(exc)

            # Remove any quotes and format
            error_message = error_message.replace("'", "").replace('"', "")

            # Return simplified error format
            return Response(
                {"error": error_message},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Return the exception as a standard error
        return Response(
            {"error": str(exc)},
            status=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        )

    # Define the schema for DELETE method
    @extend_schema(
        tags=["Users"],
        summary="Request account deletion.",
        description="""
        Requests deletion of the authenticated user's account.
        Sends a deletion confirmation email with a link to the user.
        """,
        operation_id="users_deletion_request_create",
        responses={
            status.HTTP_200_OK: UserDeletionRequestSuccessResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: UserDeletionRequestUnauthorizedResponseSerializer,
        },
    )
    def delete(self, request: Request) -> Response:
        """Handle DELETE request for account deletion.

        This method processes requests to delete a user account.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Get the user
        user = request.user

        # Generate deletion token and uid
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Store the deletion token in the database
        with transaction.atomic():
            # Update or create the deletion token
            UserDeletionToken.objects.update_or_create(
                user=user,
                defaults={"uid": uid, "token": token},
            )

        # Get scheme and domain from settings
        scheme = settings.ACTIVATION_SCHEME
        domain_part = settings.ACTIVATION_DOMAIN

        # Construct full deletion URL
        relative_deletion_path = reverse(
            "users:user-deletion-confirm",
            kwargs={"uid": uid, "token": token},
        )
        deletion_url = f"{scheme}://{domain_part}{relative_deletion_path}"

        # Prepare email context
        context = {
            "user": user,
            "deletion_link": deletion_url,
            "current_year": timezone.now().year,
            "domain_part": domain_part,
        }

        # Send deletion email
        send_templated_mail(
            template_name="users/user_deletion_request.html",
            subject="Confirm Account Deletion",
            context=context,
            recipient_list=[user.email],
        )

        # Return success response
        return Response(
            {
                "message": "Account deletion email sent successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


# User deletion confirm view
class UserDeletionConfirmView(APIView):
    """User deletion confirm view.

    This view handles the confirmation of account deletion.
    It verifies the deletion token and deletes the account.

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

    # Define the schema for DELETE method
    @extend_schema(
        tags=["Users"],
        summary="Confirm account deletion.",
        description="""
        Confirms deletion of a user account using the UID and token from the deletion link.
        This action cannot be undone.
        """,
        operation_id="users_deletion_confirm_create",
        responses={
            status.HTTP_200_OK: UserDeletionConfirmSuccessResponseSerializer,
            status.HTTP_403_FORBIDDEN: UserDeletionForbiddenResponseSerializer,
        },
    )
    def delete(self, request: Request, uid: str, token: str) -> Response:
        """Handle DELETE request for confirming account deletion.

        This method confirms deletion of a user account.

        Args:
            request (Request): The HTTP request object.
            uid (str): The base64-encoded user ID.
            token (str): The deletion token.

        Returns:
            Response: The HTTP response object.
        """

        try:
            try:
                # Get the deletion token from the database
                deletion_token = get_object_or_404(
                    UserDeletionToken.objects.select_related("user"),
                    uid=uid,
                    token=token,
                )

            except Http404:
                # Return 403 Forbidden with an error message
                return Response(
                    {"error": "Invalid or already used deletion link"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Check if the token has expired
            if deletion_token.is_expired:
                # Delete the expired token
                deletion_token.delete()

                # Return 403 Forbidden with error message
                return Response(
                    {"error": "Deletion link has expired"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Get the user associated with the token (already loaded with select_related)
            user = deletion_token.user

            # Get the user's email for sending the confirmation email
            user_email = user.email

            # Delete the user and token in a transaction
            with transaction.atomic():
                # Delete the token first (to prevent reuse)
                deletion_token.delete()

                # Delete the user
                user.delete()

            # Get domain part for the email footer from settings
            domain_part = settings.ACTIVATION_DOMAIN

            # Prepare deletion success email context
            context = {
                "email": user_email,
                "current_year": timezone.now().year,
                "domain_part": domain_part,
            }

            # Send deletion success email
            send_templated_mail(
                template_name="users/user_deletion_success.html",
                subject="Account Deleted Successfully",
                context=context,
                recipient_list=[user_email],
            )

            # Return success response
            return Response(
                {
                    "message": "Account deleted successfully",
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )

        except (TypeError, ValueError, AttributeError):
            # Return error response for specific exceptions
            return Response(
                {"error": "Invalid deletion link"},
                status=status.HTTP_403_FORBIDDEN,
            )
