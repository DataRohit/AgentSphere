# Third-party imports
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# Project imports
from apps.common.renderers import GenericJSONRenderer
from apps.users.serializers import (
    UserProfileErrorResponseSerializer,
    UserProfileResponseSerializer,
    UserProfileSerializer,
    UserProfileUpdateErrorResponseSerializer,
    UserProfileUpdateResponseSerializer,
    UserProfileUpdateSerializer,
)


# User me view
class UserMeView(APIView):
    """User me view.

    This view handles the authenticated user's profile information.
    GET: Returns the user's profile information.
    PATCH: Updates the user's profile information (username, first name, last name).
    It requires a valid JWT access token for authentication.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
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
            {"status_code": status.HTTP_401_UNAUTHORIZED, "error": str(exc)},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Define the schema for GET method
    @extend_schema(
        tags=["Users"],
        summary="Get authenticated user profile.",
        description="""
        Returns the authenticated user's profile information.
        Requires a valid JWT access token for authentication.
        """,
        responses={
            status.HTTP_200_OK: UserProfileResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: UserProfileErrorResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        """Handle GET request for user profile.

        This method returns the authenticated user's profile information.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Serialize the authenticated user
        serializer = UserProfileSerializer(request.user)

        # Return the serialized user data
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    # Define the schema for PATCH method
    @extend_schema(
        tags=["Users"],
        summary="Update authenticated user profile.",
        description="""
        Updates the authenticated user's profile information.
        Users can update their username, first name, and last name.
        Requires a valid JWT access token for authentication.
        """,
        request=UserProfileUpdateSerializer,
        responses={
            status.HTTP_200_OK: UserProfileUpdateResponseSerializer,
            status.HTTP_400_BAD_REQUEST: UserProfileUpdateErrorResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: UserProfileErrorResponseSerializer,
        },
    )
    def patch(self, request: Request) -> Response:
        """Handle PATCH request for updating user profile.

        This method updates the authenticated user's profile information.
        Users can update their username, first name, and last name.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Create serializer instance with request data and context
        serializer = UserProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        # Validate the serializer
        if serializer.is_valid():
            # Save the updated user
            serializer.save()

            # Return the updated user profile
            return Response(
                UserProfileSerializer(request.user).data,
                status=status.HTTP_200_OK,
            )

        # Return validation errors
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
