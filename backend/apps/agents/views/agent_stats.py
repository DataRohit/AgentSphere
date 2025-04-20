# Third-party imports
from django.db.models import Count, Q
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
from apps.agents.serializers.agent_stats import (
    AgentStatsAuthErrorResponseSerializer,
    AgentStatsSerializer,
    MostActiveAgentsSuccessResponseSerializer,
    MostUsedAgentsSuccessResponseSerializer,
)
from apps.common.renderers import GenericJSONRenderer


# Most used agents view
class MostUsedAgentsView(APIView):
    """View for retrieving the most used agents.

    This view allows authenticated users to retrieve the top 3 most used agents.
    Agents are ranked by how many single chats or group chats they are part of.

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
    object_label = "agents"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the most used agents view.

        This method handles exceptions for the most used agents view.

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

    # Define the schema for the GET view
    @extend_schema(
        tags=["Agents"],
        summary="Get the most used public agents.",
        description="""
        Retrieves the top 3 most used public agents.
        Agents are ranked by how many single chats or group chats they are part of.
        Only public agents are included in the results.
        """,
        responses={
            status.HTTP_200_OK: MostUsedAgentsSuccessResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: AgentStatsAuthErrorResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        """Get the most used public agents.

        This method retrieves the top 3 most used public agents.
        Agents are ranked by how many single chats or group chats they are part of.
        Only public agents are included in the results.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Get the authenticated user
        user = request.user

        # Start building the query
        query = Agent.objects.annotate(
            single_chat_count=Count("single_chats", distinct=True),
            group_chat_count=Count("group_chats", distinct=True),
        ).annotate(count=Count("single_chats", distinct=True) + Count("group_chats", distinct=True))

        # Apply access filter
        query = query.filter(Q(user=user) | Q(organization__members=user) | Q(organization__owner=user))

        # Only include public agents
        query = query.filter(is_public=True)

        # Get the top 3 most used agents
        most_used_agents = query.order_by("-count")[:3]

        # Serialize the agents
        serializer = AgentStatsSerializer(most_used_agents, many=True)

        # Return a successful response with the agents data
        return Response(
            {"agents": serializer.data},
            status=status.HTTP_200_OK,
        )


# Most active agents view
class MostActiveAgentsView(APIView):
    """View for retrieving the most active agents.

    This view allows authenticated users to retrieve the top 3 most active agents.
    Agents are ranked by how many sessions they have been part of.

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
    object_label = "agents"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the most active agents view.

        This method handles exceptions for the most active agents view.

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

    # Define the schema for the GET view
    @extend_schema(
        tags=["Agents"],
        summary="Get the most active public agents.",
        description="""
        Retrieves the top 3 most active public agents.
        Agents are ranked by how many sessions they have been part of.
        Only public agents are included in the results.
        """,
        responses={
            status.HTTP_200_OK: MostActiveAgentsSuccessResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: AgentStatsAuthErrorResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        """Get the most active public agents.

        This method retrieves the top 3 most active public agents.
        Agents are ranked by how many sessions they have been part of.
        Only public agents are included in the results.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Get the authenticated user
        user = request.user

        # Start building the query
        query = Agent.objects.annotate(
            single_chat_session_count=Count("single_chats__sessions", distinct=True),
            group_chat_session_count=Count("group_chats__sessions", distinct=True),
        ).annotate(
            count=Count("single_chats__sessions", distinct=True) + Count("group_chats__sessions", distinct=True),
        )

        # Apply access filter
        query = query.filter(Q(user=user) | Q(organization__members=user) | Q(organization__owner=user))

        # Only include public agents
        query = query.filter(is_public=True)

        # Get the top 3 most active agents
        most_active_agents = query.order_by("-count")[:3]

        # Serialize the agents
        serializer = AgentStatsSerializer(most_active_agents, many=True)

        # Return a successful response with the agents data
        return Response(
            {"agents": serializer.data},
            status=status.HTTP_200_OK,
        )
