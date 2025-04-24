# Third-party imports
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError

# Local application imports
from apps.chats.models import GroupChat, Message
from apps.chats.serializers import (
    GroupChatMessageDeleteAuthErrorResponseSerializer,
    GroupChatMessageDeleteNotFoundResponseSerializer,
    GroupChatMessageDeletePermissionDeniedResponseSerializer,
    GroupChatMessageDeleteSuccessResponseSerializer,
)
from apps.common.renderers import GenericJSONRenderer

# Get the User model
User = get_user_model()


# GroupChat message delete view
class GroupChatMessageDeleteView(APIView):
    """GroupChat message delete view.

    This view allows authorized users to delete messages in a group chat.
    Only the user who created the chat and the owner of the organization can delete messages.
    Both user and agent messages can be deleted.

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
    object_label = "message"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the group chat message delete view.

        This method handles exceptions for the group chat message delete view.

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

    # Define the schema for the DELETE view
    @extend_schema(
        tags=["Group Chat Messages"],
        summary="Delete a message in a group chat.",
        description="""
        Deletes a message in a group chat.
        Only the user who created the chat and the owner of the organization can delete messages.
        Both user and agent messages can be deleted.
        """,
        responses={
            status.HTTP_200_OK: GroupChatMessageDeleteSuccessResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: GroupChatMessageDeleteAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: GroupChatMessageDeletePermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: GroupChatMessageDeleteNotFoundResponseSerializer,
        },
    )
    def delete(self, request: Request, group_chat_id: str, message_id: str) -> Response:
        """Delete a message in a group chat.

        This method deletes a message in a group chat.
        Only the user who created the chat and the owner of the organization can delete messages.
        Both user and agent messages can be deleted.

        Args:
            request (Request): The HTTP request object.
            group_chat_id (str): The ID of the group chat.
            message_id (str): The ID of the message to delete.

        Returns:
            Response: The HTTP response object.
        """

        # Get the authenticated user
        user = request.user

        try:
            # Try to get the group chat
            group_chat = GroupChat.objects.get(id=group_chat_id)

            # Check if the user has permission to access this chat
            is_chat_creator = user == group_chat.user
            is_org_owner = group_chat.organization and user == group_chat.organization.owner

            # If the user is neither the chat creator nor the organization owner, deny permission
            if not (is_chat_creator or is_org_owner):
                # Return a permission denied error
                return Response(
                    {"error": "You do not have permission to delete messages in this chat."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            try:
                # Try to get the message
                message = Message.objects.get(id=message_id, group_chat=group_chat)

                # Delete the message
                message.delete()

                # Return 200 OK with a success message
                return Response(
                    {"message": "Message deleted successfully."},
                    status=status.HTTP_200_OK,
                )

            except Message.DoesNotExist:
                # Return a not found error
                return Response(
                    {"error": "Message not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        except GroupChat.DoesNotExist:
            # Return a not found error
            return Response(
                {"error": "Group chat not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
