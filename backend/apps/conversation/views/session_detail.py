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
from apps.conversation.models import Session
from apps.conversation.serializers.session import SessionResponseSchema
from apps.conversation.serializers.session_detail import (
    SessionDetailAuthErrorResponseSerializer,
    SessionDetailNotFoundResponseSerializer,
    SessionDetailPermissionDeniedResponseSerializer,
    SessionDetailSuccessResponseSerializer,
)

# Get the User model
User = get_user_model()


# Session detail view
class SessionDetailView(APIView):
    """View for retrieving a session by ID.

    This view allows authenticated users to retrieve a session by its ID.
    Only the user associated with the chat of the session can access it.
    It returns the session details including a WebSocket URL.

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
        """Handle exceptions for the session detail view.

        This method handles exceptions for the session detail view.

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
        tags=["Sessions"],
        summary="Get a session by ID.",
        description="""
        Retrieves a session by its ID.
        Only the user associated with the chat of the session can access it.
        Returns the session details including a WebSocket URL.
        """,
        responses={
            status.HTTP_200_OK: SessionDetailSuccessResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: SessionDetailAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: SessionDetailPermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: SessionDetailNotFoundResponseSerializer,
        },
    )
    def get(self, request: Request, session_id: str) -> Response:
        """Get a session by ID.

        This method retrieves a session by its ID.
        Only the user associated with the chat of the session can access it.
        It returns the session details including a WebSocket URL.

        Args:
            request (Request): The HTTP request object.
            session_id (str): The ID of the session.

        Returns:
            Response: The HTTP response object.
        """

        # Get the authenticated user
        user = request.user

        try:
            # Try to get the session
            session = Session.objects.get(id=session_id)

            # Check if the user has permission to access this session
            has_permission = False

            # If the session has a single chat
            if session.single_chat:
                # Check if user is the owner of the chat or the owner of the organization
                has_permission = session.single_chat.user == user or (
                    session.single_chat.organization and user == session.single_chat.organization.owner
                )

            # If the session has a group chat
            elif session.group_chat:
                # Check if the user is the owner of the organization that the chat belongs to
                has_permission = session.group_chat.organization and user == session.group_chat.organization.owner

            # If the user doesn't have permission
            if not has_permission:
                # Return a permission denied error
                return Response(
                    {"error": "You do not have permission to access this session."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Generate the WebSocket URL
            websocket_url = f"ws://{settings.ALLOWED_HOSTS[0]}/ws/conversation/session/{session.id}/"

            # Create a response serializer
            response_data = SessionResponseSchema(session).data

            # Add the WebSocket URL to the response data
            response_data["websocket_url"] = websocket_url

            # Return a successful response with the session data
            return Response(
                response_data,
                status=status.HTTP_200_OK,
            )

        except Session.DoesNotExist:
            # Return a not found error
            return Response(
                {"error": "Session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
