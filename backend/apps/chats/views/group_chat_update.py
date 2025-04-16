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
    GroupChatAuthErrorResponseSerializer,
    GroupChatNotFoundErrorResponseSerializer,
    GroupChatPermissionDeniedResponseSerializer,
    GroupChatSerializer,
    GroupChatUpdateErrorResponseSerializer,
    GroupChatUpdateSerializer,
    GroupChatUpdateSuccessResponseSerializer,
)
from apps.common.renderers import GenericJSONRenderer

# Get the User model
User = get_user_model()


# GroupChat update view
class GroupChatUpdateView(APIView):
    """GroupChat update view.

    This view allows authenticated users to update their group chats.
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
        """Handle exceptions for the group chat update view.

        This method handles exceptions for the group chat update view.

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

    # Define the schema for the PATCH view
    @extend_schema(
        tags=["Chats"],
        summary="Update a group chat.",
        description="""
        Updates an existing group chat. The user must be the owner of the chat
        or a member of the organization that the chat belongs to.
        """,
        request=GroupChatUpdateSerializer,
        responses={
            status.HTTP_200_OK: GroupChatUpdateSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: GroupChatUpdateErrorResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: GroupChatAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: GroupChatPermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: GroupChatNotFoundErrorResponseSerializer,
        },
    )
    def patch(self, request: Request, group_chat_id: str) -> Response:
        """Update a group chat.

        This method updates an existing group chat. The user must be the owner
        of the chat or a member of the organization that the chat belongs to.

        Args:
            request (Request): The HTTP request object.
            group_chat_id (str): The ID of the group chat to update.

        Returns:
            Response: The HTTP response object.

        Raises:
            NotFound: If the group chat does not exist.
            PermissionDenied: If the user does not have permission to update the chat.
        """

        try:
            # Try to get the group chat
            group_chat = GroupChat.objects.get(id=group_chat_id)

            # Check if the user has permission to update this chat
            user = request.user
            if group_chat.user != user and (
                not group_chat.organization
                or (user not in group_chat.organization.members.all() and user != group_chat.organization.owner)
            ):
                # Return a permission denied error
                return Response(
                    {"error": "You do not have permission to update this chat."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Create a serializer instance
            serializer = GroupChatUpdateSerializer(
                instance=group_chat,
                data=request.data,
                context={"request": request, "group_chat": group_chat},
                partial=True,
            )

            # Validate the serializer
            if serializer.is_valid():
                # Save the updated group chat
                updated_group_chat = serializer.save()

                # Serialize the updated group chat for the response body
                response_serializer = GroupChatSerializer(updated_group_chat)

                # Return 200 OK with the serialized group chat data
                return Response(
                    response_serializer.data,
                    status=status.HTTP_200_OK,
                )

            # Return 400 Bad Request with validation errors
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except GroupChat.DoesNotExist:
            # Return a not found error
            return Response(
                {"error": "Group chat not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
