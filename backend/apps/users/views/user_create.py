# Third-party imports
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError

# Local application imports
from apps.common.renderers import GenericJSONRenderer
from apps.common.utils import send_templated_mail
from apps.users.models import UserActivationToken
from apps.users.serializers import (
    UserCreateErrorResponseSerializer,
    UserCreateSerializer,
    UserCreateSuccessResponseSerializer,
    UserDetailSerializer,
)

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

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the user creation view.

        This method handles exceptions for the user creation view.

        Args:
            exc (Exception): The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return custom format for authentication errors
        if isinstance(exc, (AuthenticationFailed, TokenError)):
            # Return the error response
            return Response(
                {"error": str(exc)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Return the exception as a standard error
        return Response(
            {"error": str(exc)},
            status=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        )

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

            # Get scheme and domain from settings
            scheme = settings.ACTIVATION_SCHEME
            domain_part = settings.ACTIVATION_DOMAIN

            # Construct full activation URL
            activation_url = f"{scheme}://{domain_part}/auth/activate/{uid}/{token}/"

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
