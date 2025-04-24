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

# Local application imports
from apps.agents.models import Agent
from apps.agents.serializers import (
    AgentAuthErrorResponseSerializer,
    AgentDeleteNotFoundResponseSerializer,
    AgentDeletePermissionDeniedResponseSerializer,
    AgentDeleteSuccessResponseSerializer,
)
from apps.common.renderers import GenericJSONRenderer

# Get the User model
User = get_user_model()


# Agent delete view
class AgentDeleteView(APIView):
    """Agent delete view.

    This view allows users to delete their own agents.
    Only the user who created an agent can delete it.

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
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the agent delete view.

        This method handles exceptions for the agent delete view.

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

    # Define the schema
    @extend_schema(
        tags=["Agents"],
        summary="Delete an existing agent.",
        description="""
        Deletes an existing agent. Only the user who created the agent can delete it.
        """,
        responses={
            status.HTTP_200_OK: AgentDeleteSuccessResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: AgentAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: AgentDeletePermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: AgentDeleteNotFoundResponseSerializer,
        },
    )
    def delete(self, request: Request, agent_id: str) -> Response:
        """Delete an existing agent.

        This method deletes an existing agent. Only the user who created the agent can delete it.

        Args:
            request (Request): The HTTP request object.
            agent_id (str): The ID of the agent to delete.

        Returns:
            Response: The HTTP response object.

        Raises:
            NotFound: If the agent doesn't exist.
            PermissionDenied: If the user isn't the creator of the agent.
        """

        # Get the authenticated user
        user = request.user

        try:
            # Try to get the agent
            agent = Agent.objects.get(id=agent_id)

            # Check if the user is the creator of the agent
            if agent.user != user:
                # Return the error response
                return Response(
                    {"error": "You do not have permission to delete this agent."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Delete the agent
            agent.delete()

            # Return 200 OK with success message
            return Response(
                {"message": "Agent deleted successfully."},
                status=status.HTTP_200_OK,
            )

        except Agent.DoesNotExist:
            # If the agent doesn't exist, return a 404 error
            return Response(
                {"error": "Agent not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
