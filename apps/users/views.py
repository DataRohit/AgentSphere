# Third-party imports
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
from apps.common.utils import get_activation_base_url
from apps.common.utils import send_templated_mail
from apps.users.models import UserActivationToken
from apps.users.serializers import UserActivationForbiddenResponseSerializer
from apps.users.serializers import UserActivationSuccessResponseSerializer
from apps.users.serializers import UserCreateErrorResponseSerializer
from apps.users.serializers import UserCreateSerializer
from apps.users.serializers import UserCreateSuccessResponseSerializer
from apps.users.serializers import UserDetailSerializer

# Get the user model
User = get_user_model()


# User creation view
class UserCreateView(APIView):
    """User creation view.

    This view allows users to create new accounts. The user will be inactive until activated via email.
    The user will be sent an email with a link to activate their account.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Disable authentication checks for this view
    authentication_classes = []

    # Define the permission classes
    permission_classes = [AllowAny]

    # Define the object label
    object_label = "user"

    # Define the schema
    @extend_schema(
        tags=["Users"],
        summary="Register a new user account.",
        description="""
        Creates a new user account. The user will be inactive until activated via email.
        The user will be sent an email with a link to activate their account.
        """,
        request=UserCreateSerializer,
        responses={
            status.HTTP_201_CREATED: UserCreateSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: UserCreateErrorResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        """Register a new user account.

        This view allows users to create new accounts. The user will be inactive until activated via email.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Create a new user instance
        serializer = UserCreateSerializer(data=request.data)

        # Validate the serializer
        if serializer.is_valid():
            # Save the user instance
            user = serializer.save()

            # Generate activation token and uid
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # Store the activation token in the database
            UserActivationToken.objects.create(
                user=user,
                uid=uid,
                token=token,
            )

            # Get scheme and domain part from utility function
            scheme, domain_part = get_activation_base_url(request)

            # Construct full activation URL
            relative_activation_path = reverse(
                "users:user-activation",
                kwargs={"uid": uid, "token": token},
            )
            activation_url = f"{scheme}://{domain_part}{relative_activation_path}"

            # Prepare email context including domain_part
            context = {
                "user": user,
                "activation_link": activation_url,
                "current_year": timezone.now().year,
                "domain_part": domain_part,
            }

            # Send activation email using utility function
            send_templated_mail(
                template_name="users/user_activation.html",
                subject="Activate Your Account",
                context=context,
                recipient_list=[user.email],
            )

            # Serialize the created user with detailed fields for the response body
            response_serializer = UserDetailSerializer(user)

            # Return 201 Created with the serialized user data
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        # Return 400 Bad Request with validation errors
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
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

            # Get domain part for the email footer
            _, domain_part = get_activation_base_url(request)

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
