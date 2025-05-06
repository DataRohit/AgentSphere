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
    AgentListMissingParamResponseSerializer,
    AgentListNotFoundResponseSerializer,
    AgentListResponseSerializer,
    AgentSerializer,
)
from apps.common.renderers import GenericJSONRenderer
from apps.organization.models import Organization

# Get the User model
User = get_user_model()


# Agent list view
class AgentListView(APIView):
    """Agent list view.

    This view allows organization owners to list agents within their organization.
    It requires the organization_id and username parameters. Only the organization owner can
    view agents created by other members of the organization.

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
        """Handle exceptions for the agent list view.

        This method handles exceptions for the agent list view.

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

    # Define the schema for the list view
    @extend_schema(
        tags=["Agents"],
        summary="List agents within an organization by username.",
        description="""
        Lists agents within the specified organization for a specific user.
        Only the organization owner can view agents created by other members.
        Both organization_id and username parameters are mandatory.
        """,
        parameters=[
            OpenApiParameter(
                name="organization_id",
                description="Organization ID (required)",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="username",
                description="Username to filter agents by creator (required)",
                required=True,
                type=str,
            ),
        ],
        responses={
            status.HTTP_200_OK: AgentListResponseSerializer,
            status.HTTP_400_BAD_REQUEST: AgentListMissingParamResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: AgentAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: AgentAuthErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: AgentListNotFoundResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:  # noqa: PLR0911
        """List agents within an organization by username.

        This method lists agents within the specified organization for a specific user.
        Only the organization owner can view agents created by other members.
        Both organization_id and username parameters are mandatory.

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

        # Check if username is provided
        username = request.query_params.get("username")
        if not username:
            # Return 400 Bad Request if username is not provided
            return Response(
                {"error": "Missing required parameter: username"},
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

        try:
            # Get the organization
            organization = Organization.objects.get(id=organization_id)

            try:
                # Check if the target user exists
                target_user = User.objects.get(username=username)

                # Check if the user is trying to view agents created by another user
                if user.username != username:
                    # Only the organization owner can view agents created by other members
                    if organization.owner != user:
                        # Return 403 Forbidden if the user is not the organization owner
                        return Response(
                            {"error": "Only the organization owner can view agents created by other members."},
                            status=status.HTTP_403_FORBIDDEN,
                        )

                # Check if the target user is a member of the organization
                if not organization.members.filter(id=target_user.id).exists():
                    # Return 404 Not Found if the target user is not a member of the organization
                    return Response(
                        {"error": "The specified user is not a member of this organization."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                # Get agents created by the specified user in the organization
                queryset = Agent.objects.filter(organization_id=organization_id, user=target_user)

            except User.DoesNotExist:
                # Return 404 Not Found if the user doesn't exist
                return Response(
                    {"error": "User not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        except Organization.DoesNotExist:
            # Return 404 Not Found if the organization doesn't exist
            return Response(
                {"error": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

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
