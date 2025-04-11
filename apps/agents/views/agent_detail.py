# Third-party imports
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError

# Project imports
from apps.agents.models import Agent
from apps.agents.serializers import (
    AgentAuthErrorResponseSerializer,
    AgentDetailNotFoundResponseSerializer,
    AgentDetailPermissionDeniedResponseSerializer,
    AgentDetailSuccessResponseSerializer,
    AgentSerializer,
)
from apps.common.renderers import GenericJSONRenderer

# Get the User model
User = get_user_model()


# Agent detail view
class AgentDetailView(APIView):
    """Agent detail view.

    This view allows authenticated users to retrieve agent details by ID.
    Users can view:
    - Agents they own (both public and private)
    - Public agents from organizations they belong to

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
    object_label = "agent"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the agent detail view.

        This method handles exceptions for the agent detail view.

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

        # Return custom format for permission errors
        if isinstance(exc, PermissionDenied):
            # Return the error response
            return Response(
                {"error": str(exc)},
                status=status.HTTP_403_FORBIDDEN,
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

    # Define the schema for the detail view
    @extend_schema(
        tags=["Agents"],
        summary="Get agent details by ID.",
        description="""
        Retrieves the details of a specific agent by its ID.
        Users can only view:
        - Agents they own (both public and private)
        - Public agents from organizations they belong to
        """,
        responses={
            status.HTTP_200_OK: AgentDetailSuccessResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: AgentAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: AgentDetailPermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: AgentDetailNotFoundResponseSerializer,
        },
    )
    def get(self, request: Request, agent_id: str) -> Response:
        """Get agent details by ID.

        This method retrieves the details of a specific agent by its ID.
        Access is granted if:
        - The agent is owned by the user (regardless of is_public status)
        - The agent belongs to the user's organization AND is_public is true

        Args:
            request (Request): The HTTP request object.
            agent_id (str): The ID of the agent to retrieve.

        Returns:
            Response: The HTTP response object with the agent details.

        Raises:
            NotFound: If the agent does not exist.
            PermissionDenied: If the user does not have permission to view the agent.
        """

        # Get the authenticated user
        user = request.user

        try:
            # Try to get the agent
            agent = Agent.objects.get(id=agent_id)

            # If the agent is owned by the user
            if agent.user == user:
                # Return the agent details
                return Response(
                    AgentSerializer(agent).data,
                    status=status.HTTP_200_OK,
                )

            # If the agent belongs to the user's organization and is public
            if (
                agent.organization
                and (
                    user in agent.organization.members.all()
                    or user == agent.organization.owner
                )
                and agent.is_public
            ):
                # Return the agent details
                return Response(
                    AgentSerializer(agent).data,
                    status=status.HTTP_200_OK,
                )

            # If none of the access conditions are met, deny access
            return Response(
                {"error": "You do not have permission to view this agent."},
                status=status.HTTP_403_FORBIDDEN,
            )

        except Agent.DoesNotExist:
            # Return a 404 error
            return Response(
                {"error": "Agent not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
