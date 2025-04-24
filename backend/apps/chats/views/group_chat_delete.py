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
from apps.chats.models import GroupChat
from apps.chats.serializers import (
    GroupChatDeleteAuthErrorResponseSerializer,
    GroupChatDeleteNotFoundResponseSerializer,
    GroupChatDeletePermissionDeniedResponseSerializer,
    GroupChatDeleteSuccessResponseSerializer,
)
from apps.chats.tasks import delete_group_chat_messages
from apps.common.renderers import GenericJSONRenderer

# Get the User model
User = get_user_model()


# GroupChat delete view
class GroupChatDeleteView(APIView):
    """GroupChat delete view.

    This view allows authenticated users to delete a group chat by ID.
    The user must be the owner of the chat or the owner of the organization
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
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the group chat delete view.

        This method handles exceptions for the group chat delete view.

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
        tags=["Group Chats"],
        summary="Delete a group chat by ID.",
        description="""
        Deletes a group chat by ID. The user must be the owner of the chat or
        the owner of the organization that the chat belongs to.
        All associated messages will also be deleted.
        """,
        responses={
            status.HTTP_200_OK: GroupChatDeleteSuccessResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: GroupChatDeleteAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: GroupChatDeletePermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: GroupChatDeleteNotFoundResponseSerializer,
        },
    )
    def delete(self, request: Request, group_chat_id: str) -> Response:
        """Delete a group chat by ID.

        This method deletes a group chat by ID. The user must be the owner of the chat or
        the owner of the organization that the chat belongs to.
        All associated messages will also be deleted.

        Args:
            request (Request): The HTTP request object.
            group_chat_id (str): The ID of the group chat to delete.

        Returns:
            Response: The HTTP response object.
        """

        # Get the authenticated user
        user = request.user

        try:
            # Try to get the group chat
            group_chat = GroupChat.objects.get(id=group_chat_id)

            # Check if the user has permission to delete this chat
            if user not in (group_chat.user, group_chat.organization.owner):
                # Return a permission denied error
                return Response(
                    {"error": "You do not have permission to delete this chat."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Store the chat ID for the Celery task
            chat_id = str(group_chat.id)

            # Delete the chat
            group_chat.delete()

            # Delete associated messages using Celery task
            delete_group_chat_messages.delay(
                group_chat_id=chat_id,
            )

            # Return 200 OK with a success message
            return Response(
                {"message": "Chat deleted successfully."},
                status=status.HTTP_200_OK,
            )

        except GroupChat.DoesNotExist:
            # Return a not found error
            return Response(
                {"error": "Group chat not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
