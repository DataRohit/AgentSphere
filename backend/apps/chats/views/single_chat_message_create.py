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
from apps.chats.models import SingleChat
from apps.chats.serializers import (
    MessageSerializer,
    SingleChatMessageAuthErrorResponseSerializer,
    SingleChatMessageCreateErrorResponseSerializer,
    SingleChatMessageCreateSerializer,
    SingleChatMessageCreateSuccessResponseSerializer,
    SingleChatMessageNotFoundErrorResponseSerializer,
    SingleChatMessagePermissionDeniedResponseSerializer,
)
from apps.common.renderers import GenericJSONRenderer

# Get the User model
User = get_user_model()


# SingleChat message creation view
class SingleChatMessageCreateView(APIView):
    """SingleChat message creation view.

    This view allows authenticated users to create new messages in a single chat.
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
    object_label = "message"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the single chat message creation view.

        This method handles exceptions for the single chat message creation view.

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

    # Define the schema for the POST view
    @extend_schema(
        tags=["Single Chat Messages"],
        summary="Create a new message in a single chat.",
        description="""
        Creates a new message in an existing single chat. The user must be the owner of the chat
        or a member of the organization that the chat belongs to.
        """,
        request=SingleChatMessageCreateSerializer,
        responses={
            status.HTTP_201_CREATED: SingleChatMessageCreateSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: SingleChatMessageCreateErrorResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: SingleChatMessageAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: SingleChatMessagePermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: SingleChatMessageNotFoundErrorResponseSerializer,
        },
    )
    def post(self, request: Request, single_chat_id: str) -> Response:
        """Create a new message in a single chat.

        This method creates a new message in an existing single chat.
        The user must be the owner of the chat or a member of the organization
        that the chat belongs to.

        Args:
            request (Request): The HTTP request object.
            single_chat_id (str): The ID of the single chat.

        Returns:
            Response: The HTTP response object.
        """

        # Get the authenticated user
        user = request.user

        try:
            # Try to get the single chat
            single_chat = SingleChat.objects.get(id=single_chat_id)

            # Check if the user has permission to create messages in this chat
            if single_chat.user != user and (
                not single_chat.organization
                or (user not in single_chat.organization.members.all() and user != single_chat.organization.owner)
            ):
                # Return a permission denied error
                return Response(
                    {"error": "You do not have permission to create messages in this chat."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Create a new message instance
            serializer = SingleChatMessageCreateSerializer(
                data=request.data,
                context={"request": request, "single_chat": single_chat},
            )

            # Validate the serializer
            if serializer.is_valid():
                # Save the message instance
                message = serializer.save()

                # Serialize the created message for the response body
                response_serializer = MessageSerializer(message)

                # Return 201 Created with the serialized message data directly
                return Response(
                    response_serializer.data,
                    status=status.HTTP_201_CREATED,
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
