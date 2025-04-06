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
    AgentNotFoundResponseSerializer,
    AgentPermissionDeniedResponseSerializer,
    AgentSerializer,
    AgentUpdateErrorResponseSerializer,
    AgentUpdateSerializer,
    AgentUpdateSuccessResponseSerializer,
)
from apps.common.renderers import GenericJSONRenderer

# Get the User model
User = get_user_model()


# Agent update view
class AgentUpdateView(APIView):
    """Agent update view.

    This view allows users to update their own agents.
    Only the user who created an agent can update it.

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
        """Handle exceptions for the agent update view.

        This method handles exceptions for the agent update view.

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

    # Define the schema
    @extend_schema(
        tags=["Agents"],
        summary="Update an existing agent.",
        description="""
        Updates an existing agent. Only the user who created the agent can update it.
        All fields are optional - only the fields that need to be updated should be included.
        """,
        request=AgentUpdateSerializer,
        responses={
            status.HTTP_200_OK: AgentUpdateSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: AgentUpdateErrorResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: AgentAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: AgentPermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: AgentNotFoundResponseSerializer,
        },
    )
    def patch(self, request: Request, agent_id: str) -> Response:
        """Update an existing agent.

        This method updates an existing agent. Only the user who created the agent can update it.

        Args:
            request (Request): The HTTP request object.
            agent_id (str): The ID of the agent to update.

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
                    {"error": "You do not have permission to update this agent."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Create serializer with the agent and data
            serializer = AgentUpdateSerializer(agent, data=request.data, partial=True)

            # Validate the serializer
            if serializer.is_valid():
                # Save the updated agent
                updated_agent = serializer.save()

                # Serialize the updated agent for response
                response_serializer = AgentSerializer(updated_agent)

                # Return 200 OK with the updated agent data
                return Response(
                    response_serializer.data,
                    status=status.HTTP_200_OK,
                )

            # Return 400 Bad Request with validation errors
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Agent.DoesNotExist:
            # If the agent doesn't exist, return a 404 error
            return Response(
                {"error": "Agent not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
