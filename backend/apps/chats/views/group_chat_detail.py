# Third-party imports
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError

# Local application imports
from apps.chats.models import GroupChat
from apps.chats.serializers import (
    GroupChatDetailAuthErrorResponseSerializer,
    GroupChatDetailNotFoundResponseSerializer,
    GroupChatDetailPermissionDeniedResponseSerializer,
    GroupChatDetailSuccessResponseSerializer,
    GroupChatSerializer,
)
from apps.common.renderers import GenericJSONRenderer

# Get the User model
User = get_user_model()


# GroupChat detail view
class GroupChatDetailView(APIView):
    """GroupChat detail view.

    This view allows authenticated users to retrieve a group chat by ID.
    The user must be the owner of the chat or a member of the organization
    that the chat belongs to, or the chat must be public.

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
        """Handle exceptions for the group chat detail view.

        This method handles exceptions for the group chat detail view.

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

        # Return the exception as a standard error
        return Response(
            {"error": str(exc)},
            status=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        )

    # Define the schema for the GET view
    @extend_schema(
        tags=["Group Chats"],
        summary="Get a group chat by ID.",
        description="""
        Retrieves a group chat by ID. The user must be the owner of the chat,
        a member of the organization that the chat belongs to, or the chat must be public.
        """,
        responses={
            status.HTTP_200_OK: GroupChatDetailSuccessResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: GroupChatDetailAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: GroupChatDetailPermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: GroupChatDetailNotFoundResponseSerializer,
        },
    )
    def get(self, request: Request, group_chat_id: str) -> Response:
        """Get a group chat by ID.

        This method retrieves a group chat by ID. The user must be the owner
        of the chat, a member of the organization that the chat belongs to,
        or the chat must be public.

        Args:
            request (Request): The HTTP request object.
            group_chat_id (str): The ID of the group chat to retrieve.

        Returns:
            Response: The HTTP response object.

        Raises:
            NotFound: If the group chat does not exist.
            PermissionDenied: If the user does not have permission to view the chat.
        """

        try:
            # Try to get the group chat
            group_chat = GroupChat.objects.get(id=group_chat_id)

            # Check if the user has permission to view this chat
            user = request.user

            # Permission check logic:
            # Check all access conditions in a single expression:
            # 1. User is the creator of the chat, OR
            # 2. User is the organization owner, OR
            # 3. Chat is public AND user is a member of the organization
            has_permission = (
                group_chat.user == user
                or (group_chat.organization and user == group_chat.organization.owner)
                or (group_chat.is_public and group_chat.organization and user in group_chat.organization.members.all())
            )

            # If user doesn't have permission
            if not has_permission:
                # Return a permission denied error
                return Response(
                    {"error": "You do not have permission to view this chat."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Serialize the group chat for the response body
            serializer = GroupChatSerializer(group_chat)

            # Return 200 OK with the serialized group chat data
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
