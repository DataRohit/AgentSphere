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
from apps.agents.models import Agent
from apps.agents.serializers import (
    AgentAuthErrorResponseSerializer,
    AgentCreateErrorResponseSerializer,
    AgentCreateSerializer,
    AgentCreateSuccessResponseSerializer,
    AgentSerializer,
)
from apps.common.renderers import GenericJSONRenderer

# Get the User model
User = get_user_model()


# Agent creation view
class AgentCreateView(APIView):
    """Agent creation view.

    This view allows authenticated users to create new agents within an organization.
    The user must be a member of the organization to create agents within it.

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
        """Handle exceptions for the agent creation view.

        This method handles exceptions for the agent creation view.

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
        tags=["Agents"],
        summary="Create a new agent.",
        description=f"""
        Creates a new agent within an organization with the authenticated user as the creator.
        The user must be a member of the specified organization.
        A user can create a maximum of {Agent.MAX_AGENTS_PER_USER_PER_ORGANIZATION} agents per organization.
        """,
        request=AgentCreateSerializer,
        responses={
            status.HTTP_201_CREATED: AgentCreateSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: AgentCreateErrorResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: AgentAuthErrorResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        """Create a new agent.

        This method creates a new agent within an organization with the
        authenticated user as the creator.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Create a new agent instance
        serializer = AgentCreateSerializer(
            data=request.data,
            context={"request": request},
        )

        # Validate the serializer
        if serializer.is_valid():
            # Save the agent instance
            agent = serializer.save()

            # Serialize the created agent for the response body
            response_serializer = AgentSerializer(agent)

            # Return 201 Created with the serialized agent data directly
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED,
            )

        # Return 400 Bad Request with validation errors
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
