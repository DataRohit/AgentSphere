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

# Project imports
from apps.common.renderers import GenericJSONRenderer
from apps.organization.models import Organization
from apps.tools.models import MCPServer
from apps.tools.serializers import (
    MCPServerAuthErrorResponseSerializer,
    MCPServerDetailNotFoundResponseSerializer,
    MCPServerDetailPermissionDeniedResponseSerializer,
    MCPServerDetailSuccessResponseSerializer,
    MCPServerSerializer,
)

# Get the User model
User = get_user_model()


# MCPServer detail view
class MCPServerDetailView(APIView):
    """MCPServer detail view.

    This view allows authenticated users to retrieve MCP server details by ID.
    The user must be a member of the organization that the MCP server belongs to.

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
    object_label = "mcpserver"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the MCPServer detail view.

        This method handles exceptions for the MCPServer detail view.

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

    # Define the schema for the detail view
    @extend_schema(
        tags=["MCP Servers"],
        summary="Get details of an MCP server by ID.",
        description="""
        Retrieves the details of an MCP server by its ID.
        The user must be a member of the organization that the MCP server belongs to.
        Returns 404 if the MCP server is not found.
        Returns 403 if the user does not have permission to view the MCP server.
        The organization ID is specified in the URL path.
        """,
        responses={
            status.HTTP_200_OK: MCPServerDetailSuccessResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: MCPServerAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: MCPServerDetailPermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: MCPServerDetailNotFoundResponseSerializer,
        },
    )
    def get(self, request: Request, organization_id: str, mcpserver_id: str) -> Response:
        """Get details of an MCP server by ID.

        This method retrieves the details of an MCP server by its ID.
        The user must be a member of the organization that the MCP server belongs to.

        Args:
            request (Request): The HTTP request object.
            organization_id (str): The ID of the organization the MCP server belongs to.
            mcpserver_id (str): The ID of the MCP server to retrieve.

        Returns:
            Response: The HTTP response object with the MCP server details.
        """

        # Get the authenticated user
        user = request.user

        try:
            # Try to get the organization
            organization = Organization.objects.get(id=organization_id)

            # Check if the user is the owner or a member of the organization
            if user != organization.owner and user not in organization.members.all():
                # Return 403 Forbidden if the user is not a member of the organization
                return Response(
                    {"error": "You are not a member of this organization."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            try:
                # Try to get the MCP server
                mcpserver = MCPServer.objects.get(
                    id=mcpserver_id,
                    organization=organization,
                )

                # Check if the user created the MCP server
                if user == mcpserver.user:
                    # Return the MCP server details
                    return Response(
                        MCPServerSerializer(mcpserver).data,
                        status=status.HTTP_200_OK,
                    )

                # If the user did not create the MCP server, deny access
                return Response(
                    {"error": "You do not have permission to view this MCP server."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            except MCPServer.DoesNotExist:
                # Return 404 Not Found if the MCP server doesn't exist
                return Response(
                    {"error": "MCP server not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        except Organization.DoesNotExist:
            # Return 404 Not Found if the organization doesn't exist
            return Response(
                {"error": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
