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
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# Project imports
from apps.common.renderers import GenericJSONRenderer
from apps.common.utils import send_templated_mail
from apps.users.models import UserPasswordResetToken
from apps.users.serializers import (
    UserPasswordResetConfirmErrorResponseSerializer,
    UserPasswordResetConfirmSerializer,
    UserPasswordResetConfirmSuccessResponseSerializer,
    UserPasswordResetForbiddenResponseSerializer,
    UserPasswordResetRequestErrorResponseSerializer,
    UserPasswordResetRequestSerializer,
    UserPasswordResetRequestSuccessResponseSerializer,
)

# Get the user model
User = get_user_model()


# User password reset request view
class UserPasswordResetRequestView(APIView):
    """User password reset request view.

    This view handles requests to reset a user's password.
    It sends a password reset email with a link to the specified email address.

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
        summary="Request password reset.",
        description="""
        Requests password reset for a user account.
        Sends a password reset email with a link to the specified email address.
        """,
        operation_id="users_password_reset_request_create",
        request=UserPasswordResetRequestSerializer,
        responses={
            status.HTTP_200_OK: UserPasswordResetRequestSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: UserPasswordResetRequestErrorResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        """Handle POST request for password reset.

        This method processes requests to reset a user's password.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Create serializer instance with request data
        serializer = UserPasswordResetRequestSerializer(data=request.data)

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

        # Generate password reset token and uid
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Store the password reset token in the database
        with transaction.atomic():
            # Update or create the password reset token
            UserPasswordResetToken.objects.update_or_create(
                user=user,
                defaults={"uid": uid, "token": token},
            )

        # Get scheme and domain from settings
        scheme = settings.ACTIVATION_SCHEME
        domain_part = settings.ACTIVATION_DOMAIN

        # Construct full password reset URL
        relative_password_reset_path = reverse(
            "users:user-password-reset-confirm",
            kwargs={"uid": uid, "token": token},
        )
        password_reset_url = f"{scheme}://{domain_part}{relative_password_reset_path}"

        # Prepare email context
        context = {
            "user": user,
            "password_reset_link": password_reset_url,
            "current_year": timezone.now().year,
            "domain_part": domain_part,
        }

        # Send password reset email
        send_templated_mail(
            template_name="users/user_password_reset.html",
            subject="Password Reset",
            context=context,
            recipient_list=[user.email],
        )

        # Return success response
        return Response({"message": "Password reset email sent successfully."})


# User password reset confirm view
class UserPasswordResetConfirmView(APIView):
    """User password reset confirm view.

    This view handles the confirmation of password reset.
    It verifies the password reset token and resets the password.

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
        summary="Confirm password reset.",
        description="""
        Confirms password reset for a user account using the UID and token from the reset link.
        Requires setting a new password.
        """,
        operation_id="users_password_reset_confirm_create",
        request=UserPasswordResetConfirmSerializer,
        responses={
            status.HTTP_200_OK: UserPasswordResetConfirmSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: UserPasswordResetConfirmErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: UserPasswordResetForbiddenResponseSerializer,
        },
    )
    def post(self, request: Request, uid: str, token: str) -> Response:
        """Handle POST request for confirming password reset.

        This method confirms password reset for a user account and sets a new password.

        Args:
            request (Request): The HTTP request object.
            uid (str): The base64-encoded user ID.
            token (str): The password reset token.

        Returns:
            Response: The HTTP response object.
        """

        try:
            try:
                # Get the password reset token from the database
                reset_token = get_object_or_404(
                    UserPasswordResetToken.objects.select_related("user"),
                    uid=uid,
                    token=token,
                )

            except Http404:
                # Return 403 Forbidden with an error message
                return Response(
                    {"error": "Invalid or already used password reset link"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Check if the token has expired
            if reset_token.is_expired:
                # Delete the expired token
                reset_token.delete()

                # Return 403 Forbidden with error message
                return Response(
                    {"error": "Password reset link has expired"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Create serializer instance with request data
            serializer = UserPasswordResetConfirmSerializer(data=request.data)

            # Validate the serializer
            if not serializer.is_valid():
                # Return validation errors
                return Response(
                    {"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get the user associated with the token (already loaded with select_related)
            user = reset_token.user

            # Set the new password and save the user
            with transaction.atomic():
                # Set the new password
                user.set_password(serializer.validated_data["new_password"])

                # Save the user
                user.save(update_fields=["password"])

                # Delete the token since it's been used
                reset_token.delete()

            # Get domain part for the email footer from settings
            domain_part = settings.ACTIVATION_DOMAIN

            # Prepare password reset success email context
            context = {
                "user": user,
                "current_year": timezone.now().year,
                "domain_part": domain_part,
            }

            # Send password reset success email
            send_templated_mail(
                template_name="users/user_password_reset_success.html",
                subject="Password Reset Successfully",
                context=context,
                recipient_list=[user.email],
            )

            # Return success response
            return Response({"message": "Password reset successfully"})

        except (TypeError, ValueError, AttributeError):
            # Return error response for specific exceptions
            return Response(
                {"error": "Invalid password reset link"},
                status=status.HTTP_403_FORBIDDEN,
            )
