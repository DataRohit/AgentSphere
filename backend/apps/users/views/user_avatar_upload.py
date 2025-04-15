# Third-party imports
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError

# Local application imports
from apps.common.renderers import GenericJSONRenderer
from apps.users.serializers.user_avatar import (
    UserAvatarAuthErrorResponseSerializer,
    UserAvatarErrorResponseSerializer,
    UserAvatarSerializer,
    UserAvatarSuccessResponseSerializer,
)
from apps.users.serializers.user_profile import UserProfileSerializer

# Get the User model
User = get_user_model()


# User avatar upload view
class UserAvatarUploadView(APIView):
    """User avatar upload view.

    This view allows users to upload an avatar for their profile.
    If the user already has an avatar, the existing avatar is deleted and replaced.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        parser_classes (list): The parser classes for handling file uploads.
        object_label (str): The object label for the response.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Define the permission classes - require authentication
    permission_classes = [IsAuthenticated]

    # Define the parser classes for handling file uploads
    parser_classes = [MultiPartParser, FormParser]

    # Define the object label
    object_label = "user"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the user avatar upload view.

        This method handles exceptions for the user avatar upload view.

        Args:
            exc: The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return custom format for authentication errors
        if isinstance(exc, (AuthenticationFailed, TokenError)):
            # Return the exception as a standard error
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
        summary="Upload or update a user avatar.",
        description="""
        Uploads or updates the avatar for the authenticated user.
        If the user already has an avatar, it will be deleted and replaced.
        The avatar file must be a valid jpg, jpeg, or png image.
        """,
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {"avatar": {"type": "string", "format": "binary"}},
            },
        },
        responses={
            status.HTTP_200_OK: UserAvatarSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: UserAvatarErrorResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: UserAvatarAuthErrorResponseSerializer,
        },
    )
    def put(self, request: Request) -> Response:
        """Upload or update a user avatar.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Get the authenticated user
        user = request.user

        # Create a serializer for the avatar upload
        serializer = UserAvatarSerializer(data=request.data)

        # Validate the serializer
        if serializer.is_valid():
            # Get the uploaded avatar file
            avatar_file = serializer.validated_data["avatar"]

            # Check if the user already has an avatar
            if user.avatar:
                # Delete the existing avatar
                user.avatar.delete(save=False)

            # Get the file extension
            file_extension = avatar_file.name.split(".")[-1].lower()

            # Create a new filename using the user ID
            new_filename = f"{user.id}.{file_extension}"

            # Update the avatar file name before saving
            avatar_file.name = new_filename

            # Update the user with the new avatar
            user.avatar = avatar_file
            user.save()

            # Serialize the updated user for the response body
            response_serializer = UserProfileSerializer(user)

            # Return 200 OK with the serialized user data
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK,
            )

        # Return 400 Bad Request with validation errors
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
