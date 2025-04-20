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
from apps.conversation.serializers.session_deactivate import (
    SessionDeactivateAuthErrorResponseSerializer,
    SessionDeactivateNotFoundResponseSerializer,
    SessionDeactivatePermissionDeniedResponseSerializer,
    SessionDeactivateSuccessResponseSerializer,
)

# Get the User model
User = get_user_model()


# Session deactivate view
class SessionDeactivateView(APIView):
    """View for deactivating a session.

    This view allows authenticated users to deactivate a session.
    Only the user associated with the chat or the owner of the organization can deactivate the session.

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
    def handle_exception(self, exc):
        """Handle exceptions for the session deactivation view.

        This method handles exceptions for the session deactivation view.

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

        # Return the exception as a standard error
        return Response(
            {"error": str(exc)},
            status=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        )

    # Define the schema for the POST view
    @extend_schema(
        tags=["Sessions"],
        summary="Deactivate a session.",
        description="""
        Deactivates a session by its ID.
        Only the user associated with the chat or the owner of the organization can deactivate the session.
        """,
        responses={
            status.HTTP_200_OK: SessionDeactivateSuccessResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: SessionDeactivateAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: SessionDeactivatePermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: SessionDeactivateNotFoundResponseSerializer,
        },
    )
    def post(self, request: Request, session_id: str) -> Response:
        """Deactivate a session.

        This method deactivates a session by its ID.
        Only the user associated with the chat or the owner of the organization can deactivate the session.

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

            # Check if the user has permission to deactivate this session
            has_permission = False

            # If the session has a single chat
            if session.single_chat:
                # Check if the user is the owner of the single chat or the owner of the organization
                if session.single_chat.user == user or (
                    session.single_chat.organization and user == session.single_chat.organization.owner
                ):
                    has_permission = True

            # If the session has a group chat
            elif session.group_chat:
                # Check if the user is the owner of the organization that the chat belongs to
                if session.group_chat.organization and user == session.group_chat.organization.owner:
                    has_permission = True

            # If the user doesn't have permission
            if not has_permission:
                # Return a permission denied error
                return Response(
                    {"error": "You do not have permission to deactivate this session."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Deactivate the session
            session.is_active = False
            session.save()

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
