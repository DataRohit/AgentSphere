# Third-party imports
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError

# Local application imports
from apps.chats.models import SingleChat
from apps.chats.serializers import (
    SingleChatAuthErrorResponseSerializer,
    SingleChatNotFoundErrorResponseSerializer,
    SingleChatPermissionDeniedResponseSerializer,
    SingleChatSerializer,
    SingleChatUpdateErrorResponseSerializer,
    SingleChatUpdateSerializer,
    SingleChatUpdateSuccessResponseSerializer,
)
from apps.common.renderers import GenericJSONRenderer

# Get the User model
User = get_user_model()


# SingleChat update view
class SingleChatUpdateView(APIView):
    """SingleChat update view.

    This view allows authenticated users to update their single chats.
    The user must be the owner of the chat or a member of the organization
    that the chat belongs to.

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
    object_label = "chat"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the single chat update view.

        This method handles exceptions for the single chat update view.

        Args:
            exc: The exception that occurred.

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

        # Return custom format for not found errors
        if isinstance(exc, NotFound):
            # Return the error response
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Return custom format for permission denied errors
        if isinstance(exc, PermissionDenied):
            # Return the error response
            return Response(
                {"error": str(exc)},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Return the exception as a standard error
        return Response(
            {"error": str(exc)},
            status=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        )

    # Define the schema for the PATCH view
    @extend_schema(
        tags=["Single Chats"],
        summary="Update a single chat.",
        description="""
        Updates an existing single chat. The user must be the owner of the chat
        or a member of the organization that the chat belongs to.
        """,
        request=SingleChatUpdateSerializer,
        responses={
            status.HTTP_200_OK: SingleChatUpdateSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: SingleChatUpdateErrorResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: SingleChatAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: SingleChatPermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: SingleChatNotFoundErrorResponseSerializer,
        },
    )
    def patch(self, request: Request, single_chat_id: str) -> Response:
        """Update a single chat.

        This method updates an existing single chat. The user must be the owner
        of the chat or a member of the organization that the chat belongs to.

        Args:
            request (Request): The HTTP request object.
            single_chat_id (str): The ID of the single chat to update.

        Returns:
            Response: The HTTP response object.

        Raises:
            NotFound: If the single chat does not exist.
            PermissionDenied: If the user does not have permission to update the chat.
        """

        try:
            # Try to get the single chat
            single_chat = SingleChat.objects.get(id=single_chat_id)

            # Check if the user has permission to update this chat
            user = request.user
            if single_chat.user != user and (
                not single_chat.organization
                or (user not in single_chat.organization.members.all() and user != single_chat.organization.owner)
            ):
                # Return a permission denied error
                return Response(
                    {"error": "You do not have permission to update this chat."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Create a serializer instance
            serializer = SingleChatUpdateSerializer(
                instance=single_chat,
                data=request.data,
                context={"request": request, "single_chat": single_chat},
                partial=True,
            )

            # Validate the serializer
            if serializer.is_valid():
                # Save the updated single chat
                updated_single_chat = serializer.save()

                # Serialize the updated single chat for the response body
                response_serializer = SingleChatSerializer(updated_single_chat)

                # Return 200 OK with the serialized single chat data
                return Response(
                    response_serializer.data,
                    status=status.HTTP_200_OK,
                )

            # Return 400 Bad Request with validation errors
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except SingleChat.DoesNotExist:
            # Return a not found error
            return Response(
                {"error": "Single chat not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
