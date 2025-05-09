# Third-party imports
from django.conf import settings
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
from apps.common.renderers import GenericJSONRenderer
from apps.conversation.serializers import (
    SessionAuthErrorResponseSerializer,
    SessionCreateErrorResponseSerializer,
    SessionCreateSerializer,
    SessionCreateSuccessResponseSerializer,
    SessionNotFoundErrorResponseSerializer,
    SessionPermissionDeniedResponseSerializer,
)
from apps.conversation.serializers.session import SessionResponseSchema

# Get the User model
User = get_user_model()


# Session create view
class SessionCreateView(APIView):
    """View for creating a new session.

    This view allows authenticated users to create a new session for a chat.
    It accepts a chat_id parameter and creates a session for the specified chat.
    It returns a WebSocket URL that can be used to connect to the session.

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
    object_label = "session"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the session creation view.

        This method handles exceptions for the session creation view.

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
        tags=["Sessions"],
        summary="Create a new session for a chat.",
        description="""
        Creates a new session for the specified chat (single or group).
        The chat_id and llm_id are provided in the request body.
        The user must have permission to access the chat.
        Only one active session can exist for a chat at a time.
        Returns a WebSocket URL that can be used to connect to the session.
        """,
        request=SessionCreateSerializer,
        responses={
            status.HTTP_201_CREATED: SessionCreateSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: SessionCreateErrorResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: SessionAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: SessionPermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: SessionNotFoundErrorResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        """Create a new session for a chat.

        This method creates a new session for the specified chat (single or group).
        It returns a WebSocket URL that can be used to connect to the session.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Create a serializer with the request data
        serializer = SessionCreateSerializer(
            data=request.data,
            context={"request": request},
        )

        # Validate the serializer
        if serializer.is_valid():
            # Create a new session
            session = serializer.save()

            # Generate the WebSocket URL
            websocket_url = f"{settings.DJANGO_WEBSOCKET_HOST}/conversation/session/{session.id}/"

            # Create a response serializer
            response_data = SessionResponseSchema(session).data

            # Add the WebSocket URL to the response data
            response_data["websocket_url"] = websocket_url

            # Return a successful response with the session data
            return Response(
                response_data,
                status=status.HTTP_201_CREATED,
            )

        # Return an error response with the validation errors
        return Response(
            {"error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
