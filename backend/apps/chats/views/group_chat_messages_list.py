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
    GroupChatMessagesListAuthErrorResponseSerializer,
    GroupChatMessagesListNotFoundResponseSerializer,
    GroupChatMessagesListPermissionDeniedResponseSerializer,
    GroupChatMessagesListSuccessResponseSerializer,
    MessageSerializer,
)
from apps.common.renderers import GenericJSONRenderer

# Get the User model
User = get_user_model()


# GroupChat messages list view
class GroupChatMessagesListView(APIView):
    """GroupChat messages list view.

    This view allows authorized users to list messages in a group chat.
    Access permissions:
    - If the chat is public: user who created the chat, the org owner & any other member of org can get the list of messages
    - If the chat is not public: only the user who created the chat & the org owner can get the list of messages

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        object_label (str): The object label for the response.
    """  # noqa: E501

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Define the permission classes - require authentication
    permission_classes = [IsAuthenticated]

    # Define the object label
    object_label = "messages"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the group chat messages list view.

        This method handles exceptions for the group chat messages list view.

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

    # Define the schema for the GET view
    @extend_schema(
        tags=["Group Chat Messages"],
        summary="List messages in a group chat.",
        description="""
        Lists all messages in a group chat.
        Access permissions:
        - If the chat is public: user who created the chat, the org owner & any other member of org can get the list of messages
        - If the chat is not public: only the user who created the chat & the org owner can get the list of messages
        """,  # noqa: E501
        responses={
            status.HTTP_200_OK: GroupChatMessagesListSuccessResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: GroupChatMessagesListAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: GroupChatMessagesListPermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: GroupChatMessagesListNotFoundResponseSerializer,
        },
    )
    def get(self, request: Request, group_chat_id: str) -> Response:
        """List messages in a group chat.

        This method lists all messages in a group chat.
        Access permissions:
        - If the chat is public: user who created the chat, the org owner & any other member of org can get the list of messages
        - If the chat is not public: only the user who created the chat & the org owner can get the list of messages

        Args:
            request (Request): The HTTP request object.
            group_chat_id (str): The ID of the group chat.

        Returns:
            Response: The HTTP response object with the list of messages.
        """  # noqa: E501

        # Get the authenticated user
        user = request.user

        try:
            # Try to get the group chat
            group_chat = GroupChat.objects.get(id=group_chat_id)

            # Check if the user has permission to view messages in this chat
            is_chat_creator = user == group_chat.user
            is_org_owner = group_chat.organization and user == group_chat.organization.owner
            is_org_member = group_chat.organization and user in group_chat.organization.members.all()

            # If the chat is not public, only the creator and org owner can view messages
            if not group_chat.is_public and not (is_chat_creator or is_org_owner):
                # Return a permission denied error
                return Response(
                    {"error": "You do not have permission to view messages in this private chat."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # If the chat is public, the creator, org owner, and org members can view messages
            if group_chat.is_public and not (is_chat_creator or is_org_owner or is_org_member):
                # Return a permission denied error
                return Response(
                    {"error": "You do not have permission to view messages in this chat."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Get all messages for this chat
            messages = Message.objects.filter(group_chat=group_chat).order_by("created_at")

            # Check if any messages were found
            if not messages.exists():
                # Return a not found error
                return Response(
                    {"error": "No messages found in this chat."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Serialize the messages
            serializer = MessageSerializer(messages, many=True)

            # Return the serialized messages
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        except GroupChat.DoesNotExist:
            # Return a not found error
            return Response(
                {"error": "Group chat not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
