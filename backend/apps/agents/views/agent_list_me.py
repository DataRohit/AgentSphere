# Third-party imports
from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiParameter, extend_schema
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
    AgentListMeResponseSerializer,
    AgentListMissingParamResponseSerializer,
    AgentListNotFoundResponseSerializer,
    AgentSerializer,
)
from apps.common.renderers import GenericJSONRenderer

# Get the User model
User = get_user_model()


# Agent list me view
class AgentListMeView(APIView):
    """Agent list me view.

    This view allows authenticated users to list all agents they have created.
    It requires the organization_id parameter.

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
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the agent list me view.

        This method handles exceptions for the agent list me view.

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

    # Define the schema for the list me view
    @extend_schema(
        tags=["Agents"],
        summary="List agents created by the current user.",
        description="""
        Lists all agents created by the authenticated user.
        Requires organization_id parameter.
        Returns 404 if no agents are found matching the criteria.
        """,
        parameters=[
            OpenApiParameter(
                name="organization_id",
                description="Organization ID (required)",
                required=True,
                type=str,
            ),
        ],
        responses={
            status.HTTP_200_OK: AgentListMeResponseSerializer,
            status.HTTP_400_BAD_REQUEST: AgentListMissingParamResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: AgentAuthErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: AgentListNotFoundResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        """List agents created by the current user.

        This method lists all agents created by the authenticated user.
        It requires the organization_id parameter.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object with the list of agents.
        """

        # Get the authenticated user
        user = request.user

        # Check if organization_id is provided
        organization_id = request.query_params.get("organization_id")
        if not organization_id:
            # Return 400 Bad Request if organization_id is not provided
            return Response(
                {"error": "Missing required parameter: organization_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the user's organizations
        user_organizations = user.organizations.all()

        # Check if the user is a member of the specified organization
        if not user_organizations.filter(id=organization_id).exists():
            # Return 404 Not Found if the user is not a member of the organization
            return Response(
                {"error": "No agents found matching the criteria."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Build query for user's agents in the specified organization
        queryset = Agent.objects.filter(user=user, organization_id=organization_id)

        # Check if any agents were found
        if not queryset.exists():
            # Return 404 Not Found if no agents match the criteria
            return Response(
                {"error": "No agents found matching the criteria."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Serialize the agents
        serializer = AgentSerializer(queryset, many=True)

        # Return the serialized agents directly
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
