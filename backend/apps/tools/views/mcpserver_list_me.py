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
from apps.common.renderers import GenericJSONRenderer
from apps.organization.models import Organization
from apps.tools.models import MCPServer
from apps.tools.serializers import (
    MCPServerAuthErrorResponseSerializer,
    MCPServerListMeResponseSerializer,
    MCPServerListMissingParamResponseSerializer,
    MCPServerListNotFoundResponseSerializer,
    MCPServerSerializer,
)
from apps.tools.utils.mcp_client import fetch_mcp_tools

# Get the User model
User = get_user_model()


# MCPServer list me view
class MCPServerListMeView(APIView):
    """MCPServer list me view.

    This view allows authenticated users to list all MCP servers they have created.
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
    object_label = "mcpservers"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the MCPServer list me view.

        This method handles exceptions for the MCPServer list me view.

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
        tags=["MCP Servers"],
        summary="List MCP servers created by the current user.",
        description="""
        Lists all MCP servers created by the authenticated user.
        Requires organization_id parameter.
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
            status.HTTP_200_OK: MCPServerListMeResponseSerializer,
            status.HTTP_400_BAD_REQUEST: MCPServerListMissingParamResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: MCPServerAuthErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: MCPServerListNotFoundResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        """List MCP servers created by the current user.

        This method lists all MCP servers created by the authenticated user.
        It requires the organization_id parameter.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object with the list of MCP servers.
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

        try:
            # Try to get the organization
            organization = Organization.objects.get(id=organization_id)

            # Check if the user is the owner or a member of the organization
            if user != organization.owner and user not in organization.members.all():
                # Return 404 Not Found if the user is not a member of the organization
                return Response(
                    {"error": "No MCP servers found matching the criteria."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Build query for user's MCP servers in the specified organization
            queryset = MCPServer.objects.filter(user=user, organization=organization)

        except Organization.DoesNotExist:
            # Return 404 Not Found if the organization doesn't exist
            return Response(
                {"error": "No MCP servers found matching the criteria."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if any MCP servers were found
        if not queryset.exists():
            # Return 404 Not Found if no MCP servers match the criteria
            return Response(
                {"error": "No MCP servers found matching the criteria."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Convert queryset to list to avoid re-fetching from database
        mcpserver_list = list(queryset)

        # Traverse the MCP servers
        for mcpserver in mcpserver_list:
            # Fetch tools from the MCP server
            fetch_mcp_tools(mcpserver)

        # Serialize the MCP servers
        serializer = MCPServerSerializer(mcpserver_list, many=True)

        # Return the serialized MCP servers directly
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
