# Third-party imports
from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# Local application imports
from apps.common.renderers import GenericJSONRenderer
from apps.common.utils import send_templated_mail
from apps.users.serializers import (
    UserDeactivateErrorResponseSerializer,
    UserDeactivateSerializer,
    UserDeactivateSuccessResponseSerializer,
    UserProfileErrorResponseSerializer,
)


# User deactivate view
class UserDeactivateView(APIView):
    """User deactivate view.

    This view handles deactivating the authenticated user's account.
    POST: Deactivates the user's account after password verification.
    It requires a valid JWT access token for authentication.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        object_label (str): The object label for the response.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Define the permission classes
    permission_classes = [IsAuthenticated]

    # Define the object label
    object_label = "user"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the user me view.

        This method handles exceptions for the user me view.

        Args:
            exc: The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return custom format for authentication errors
        return Response(
            {
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": str(exc.detail.get("detail")),
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Define the schema for POST method
    @extend_schema(
        tags=["Users"],
        summary="Deactivate authenticated user account.",
        description="""
        Deactivates the authenticated user's account.
        Requires the current password to be entered twice for verification.
        This action cannot be undone through the API.
        """,
        request=UserDeactivateSerializer,
        responses={
            status.HTTP_200_OK: UserDeactivateSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: UserDeactivateErrorResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: UserProfileErrorResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        """Handle POST request for deactivating user account.

        This method deactivates the authenticated user's account after verifying their password.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Get the user
        user = request.user

        # Check if the user is already inactive
        if not user.is_active:
            return Response(
                {"error": "This account is already inactive."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create serializer instance with request data and context
        serializer = UserDeactivateSerializer(
            data=request.data,
            context={"request": request},
        )

        # Validate the serializer
        if serializer.is_valid():
            # Deactivate the user account
            user.is_active = False
            user.save(update_fields=["is_active"])

            # Send account deactivation email
            context = {
                "user": user,
                "current_year": timezone.now().year,
                "domain_part": settings.ACTIVATION_DOMAIN,
            }

            # Send deactivation email
            send_templated_mail(
                template_name="users/user_deactivation.html",
                subject="Account Deactivated",
                context=context,
                recipient_list=[user.email],
            )

            # Return success response
            return Response(
                {"message": "Account deactivated successfully."},
                status=status.HTTP_200_OK,
            )

        # Return validation errors
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
