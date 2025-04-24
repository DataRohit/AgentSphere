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
from apps.chats.models import Message, SingleChat
from apps.chats.serializers import (
    MessageSerializer,
    SingleChatMessageUpdateAuthErrorResponseSerializer,
    SingleChatMessageUpdateErrorResponseSerializer,
    SingleChatMessageUpdateNotFoundErrorResponseSerializer,
    SingleChatMessageUpdatePermissionDeniedResponseSerializer,
    SingleChatMessageUpdateSerializer,
    SingleChatMessageUpdateSuccessResponseSerializer,
)
from apps.common.renderers import GenericJSONRenderer

# Get the User model
User = get_user_model()


# SingleChat message update view
class SingleChatMessageUpdateView(APIView):
    """SingleChat message update view.

    This view allows authorized users to update messages in a single chat.
    Only the user who created the chat and the owner of the organization can update messages.
    The user can only update user messages, while the organization owner can update both user and agent messages.
    Only the content field can be updated.

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
        """Handle exceptions for the single chat message update view.

        This method handles exceptions for the single chat message update view.

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

    # Define the schema for the PATCH view
    @extend_schema(
        tags=["Single Chat Messages"],
        summary="Update a message in a single chat.",
        description="""
        Updates an existing message in a single chat.
        Only the user who created the chat and the owner of the organization can update messages.
        The user can only update user messages, while the organization owner can update both user and agent messages.
        Only the content field can be updated.
        """,
        request=SingleChatMessageUpdateSerializer,
        responses={
            status.HTTP_200_OK: SingleChatMessageUpdateSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: SingleChatMessageUpdateErrorResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: SingleChatMessageUpdateAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: SingleChatMessageUpdatePermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: SingleChatMessageUpdateNotFoundErrorResponseSerializer,
        },
    )
    def patch(self, request: Request, single_chat_id: str, message_id: str) -> Response:  # noqa: PLR0911
        """Update a message in a single chat.

        This method updates an existing message in a single chat.
        Only the user who created the chat and the owner of the organization can update messages.
        The user can only update user messages, while the organization owner can update both user and agent messages.
        Only the content field can be updated.

        Args:
            request (Request): The HTTP request object.
            single_chat_id (str): The ID of the single chat.
            message_id (str): The ID of the message to update.

        Returns:
            Response: The HTTP response object.
        """

        # Get the authenticated user
        user = request.user

        try:
            # Try to get the single chat
            single_chat = SingleChat.objects.get(id=single_chat_id)

            # Check if the user has permission to access this chat
            if single_chat.user != user and (
                not single_chat.organization
                or (user not in single_chat.organization.members.all() and user != single_chat.organization.owner)
            ):
                # Return a permission denied error
                return Response(
                    {"error": "You do not have permission to access this chat."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            try:
                # Try to get the message
                message = Message.objects.get(id=message_id, single_chat=single_chat)

                # Check if the user is the chat creator or organization owner
                is_org_owner = single_chat.organization and user == single_chat.organization.owner
                is_chat_creator = user == single_chat.user

                # If the user is neither the chat creator nor the organization owner, deny permission
                if not (is_chat_creator or is_org_owner):
                    # Return a permission denied error
                    return Response(
                        {"error": "You do not have permission to update this message."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                # If the message is from an agent and the user is not the organization owner, deny permission
                if message.sender == Message.SenderType.AGENT and not is_org_owner:
                    # Return a permission denied error
                    return Response(
                        {"error": "Only the organization owner can update agent messages."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                # If the message is from a user and the user is not the chat creator, deny permission
                if message.sender == Message.SenderType.USER and not is_chat_creator and not is_org_owner:
                    # Return a permission denied error
                    return Response(
                        {"error": "Only the chat creator can update user messages."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                # Create a serializer instance
                serializer = SingleChatMessageUpdateSerializer(
                    instance=message,
                    data=request.data,
                    context={"request": request, "message": message},
                    partial=True,
                )

                # Validate the serializer
                if serializer.is_valid():
                    # Save the updated message
                    updated_message = serializer.save()

                    # Serialize the updated message for the response body
                    response_serializer = MessageSerializer(updated_message)

                    # Return 200 OK with the serialized message data
                    return Response(
                        response_serializer.data,
                        status=status.HTTP_200_OK,
                    )

                # Return 400 Bad Request with validation errors
                return Response(
                    {"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            except Message.DoesNotExist:
                # Return a not found error
                return Response(
                    {"error": "Message not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        except SingleChat.DoesNotExist:
            # Return a not found error
            return Response(
                {"error": "Single chat not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
