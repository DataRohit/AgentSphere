# Third-party imports
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError

# Local application imports
from apps.agents.models import Agent
from apps.common.renderers import GenericJSONRenderer
from apps.conversation.models import Session
from apps.conversation.serializers.session import SessionResponseSchema
from apps.conversation.serializers.session_list import (
    SessionCountSuccessResponseSerializer,
    SessionListAuthErrorResponseSerializer,
    SessionListMissingParamResponseSerializer,
    SessionListPermissionDeniedResponseSerializer,
    SessionListSuccessResponseSerializer,
)

# Get the User model
User = get_user_model()


# Base session list view
class BaseSessionListView(APIView):
    """Base view for listing active sessions.

    This view provides common functionality for listing active sessions.
    It handles filtering by chat type, user ID, and agent ID.

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
    object_label = "sessions"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the session list view.

        This method handles exceptions for the session list view.

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

    # Get filtered active sessions
    def get_filtered_sessions(self, request: Request) -> tuple:
        """Get filtered active sessions.

        This method filters active sessions based on the request parameters.
        It handles filtering by chat type, user ID, and agent ID.

        Args:
            request (Request): The HTTP request object.

        Returns:
            tuple: A tuple containing the filtered sessions and any error response.
        """

        # Get the authenticated user
        user = request.user

        # Initialize the base queryset for active sessions
        sessions = Session.objects.filter(is_active=True)

        # Get the chat type filter
        chat_type = request.query_params.get("chat_type")
        if chat_type:
            # Filter sessions by chat type
            if chat_type.lower() == "single":
                # Filter sessions by single chat
                sessions = sessions.filter(single_chat__isnull=False)

            elif chat_type.lower() == "group":
                # Filter sessions by group chat
                sessions = sessions.filter(group_chat__isnull=False)

        # Get the user ID filter
        user_id = request.query_params.get("user_id")
        if user_id:
            # Only organization owners can filter by user ID
            if not user.organizations_owned.exists():
                # Return a permission denied error
                return None, Response(
                    {"error": "Only organization owners can filter by user ID."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Filter sessions by user ID
            sessions = sessions.filter(
                Q(single_chat__user__id=user_id) | Q(group_chat__organization__members__id=user_id),
            ).distinct()

        # Get the agent ID filter
        agent_id = request.query_params.get("agent_id")
        if agent_id:
            try:
                # Try to get the agent
                agent = Agent.objects.get(id=agent_id)

                # Check if the user has permission to view sessions with this agent
                has_permission = (
                    agent.user == user
                    or (agent.organization and user == agent.organization.owner)
                    or (agent.is_public and agent.organization and user in agent.organization.members.all())
                )

                # If the user doesn't have permission
                if not has_permission:
                    # Return a permission denied error
                    return None, Response(
                        {"error": "You do not have permission to view sessions with this agent."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                # Filter sessions by agent ID
                sessions = sessions.filter(
                    Q(single_chat__agent__id=agent_id) | Q(group_chat__agents__id=agent_id),
                ).distinct()

            except Agent.DoesNotExist:
                # Return a not found error
                return None, Response(
                    {"error": "Agent not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # Return the filtered sessions and no error
        return sessions, None


# Session list view
class SessionListView(BaseSessionListView):
    """View for listing active sessions.

    This view allows authenticated users to list active sessions.
    It handles filtering by chat type, user ID, and agent ID.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        object_label (str): The object label for the response.
    """

    # Define the schema for the GET view
    @extend_schema(
        tags=["Sessions"],
        summary="List active sessions.",
        description="""
        Lists active sessions with optional filtering.

        Filters:
        - chat_type: Filter by chat type (single or group).
        - user_id: Filter by user ID (only organization owners can use this).
        - agent_id: Filter by agent ID (requires permission to view the agent).
        """,
        responses={
            status.HTTP_200_OK: SessionListSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: SessionListMissingParamResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: SessionListAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: SessionListPermissionDeniedResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        """List active sessions.

        This method lists active sessions with optional filtering.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Get filtered sessions
        sessions, error_response = self.get_filtered_sessions(request)

        # If there was an error
        if error_response:
            # Return the error response
            return error_response

        # Generate WebSocket URLs for each session
        session_data = []
        for session in sessions:
            # Create a response serializer
            data = SessionResponseSchema(session).data

            # Add the WebSocket URL to the response data
            data["websocket_url"] = f"ws://{settings.ALLOWED_HOSTS[0]}/ws/conversation/session/{session.id}/"

            # Add the session data to the list
            session_data.append(data)

        # Return a successful response with the session data
        return Response(
            {"sessions": session_data},
            status=status.HTTP_200_OK,
        )


# Session count view
class SessionCountView(BaseSessionListView):
    """View for counting active sessions.

    This view allows authenticated users to count active sessions.
    It handles filtering by chat type, user ID, and agent ID.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        object_label (str): The object label for the response.
    """

    # Define the schema for the GET view
    @extend_schema(
        tags=["Sessions"],
        summary="Count active sessions.",
        description="""
        Counts active sessions with optional filtering.

        Filters:
        - chat_type: Filter by chat type (single or group).
        - user_id: Filter by user ID (only organization owners can use this).
        - agent_id: Filter by agent ID (requires permission to view the agent).
        """,
        responses={
            status.HTTP_200_OK: SessionCountSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: SessionListMissingParamResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: SessionListAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: SessionListPermissionDeniedResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        """Count active sessions.

        This method counts active sessions with optional filtering.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Get filtered sessions
        sessions, error_response = self.get_filtered_sessions(request)

        # If there was an error
        if error_response:
            # Return the error response
            return error_response

        # Count the sessions
        count = sessions.count()

        # Return a successful response with the count
        return Response(
            {"sessions": {"count": count}},
            status=status.HTTP_200_OK,
        )
