# Third-party imports
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# Local application imports
from apps.common.renderers import GenericJSONRenderer
from apps.common.utils import send_templated_mail
from apps.users.models import UserActivationToken
from apps.users.serializers import (
    ResendActivationEmailSerializer,
    ResendActivationErrorResponseSerializer,
    ResendActivationNotFoundResponseSerializer,
    ResendActivationSuccessResponseSerializer,
)

# Get the user model
User = get_user_model()


# Resend activation email view
class ResendActivationEmailView(APIView):
    """View to resend the activation email for an inactive user.

    Accepts an email address via POST request. If a matching inactive user is found,
    it generates a new activation token, updates the database, and resends the activation email.
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
        summary="Resend activation email.",
        description="""
        Resends the activation email to a user if their account is inactive.
        The user must be inactive to receive a new activation email.
        """,
        request=ResendActivationEmailSerializer,
        responses={
            status.HTTP_200_OK: ResendActivationSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: ResendActivationErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: ResendActivationNotFoundResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        """Handle POST request to resend activation email.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Validate the serializer
        serializer = ResendActivationEmailSerializer(data=request.data)

        # If the serializer is not valid
        if not serializer.is_valid():
            # Return 400 Bad Request with validation errors
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the email from the validated data
        email = serializer.validated_data["email"]

        try:
            # Get the user from the database
            user = User.objects.get(email=email)

            # Check if the user is already active
            if user.is_active:
                # Return 400 Bad Request with an error message
                return Response(
                    {
                        "errors": {
                            "email": ["User account is already active."],
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

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

            # Return 200 OK with a success message
            return Response(
                {"message": "Activation email sent successfully."},
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            # Return 404 Not Found with an error message
            return Response(
                {
                    "errors": {
                        "email": ["User with this email address does not exist."],
                    },
                },
                status=status.HTTP_404_NOT_FOUND,
            )
