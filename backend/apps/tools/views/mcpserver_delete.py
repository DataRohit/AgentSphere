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
from apps.common.renderers import GenericJSONRenderer
from apps.tools.models import MCPServer
from apps.tools.serializers import (
    MCPServerAuthErrorResponseSerializer,
    MCPServerDeleteNotFoundResponseSerializer,
    MCPServerDeletePermissionDeniedResponseSerializer,
    MCPServerDeleteSuccessResponseSerializer,
)

# Get the User model
User = get_user_model()


# MCPServer delete view
class MCPServerDeleteView(APIView):
    """MCPServer delete view.

    This view allows users to delete their own MCP servers.
    Only the user who created an MCP server can delete it.

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
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the MCPServer delete view.

        This method handles exceptions for the MCPServer delete view.

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

        # Call the parent method for other exceptions
        return super().handle_exception(exc)

    # Define the schema
    @extend_schema(
        tags=["MCP Servers"],
        summary="Delete an existing MCP server.",
        description="""
        Deletes an existing MCP server. Only the user who created the MCP server can delete it.
        """,
        responses={
            status.HTTP_200_OK: MCPServerDeleteSuccessResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: MCPServerAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: MCPServerDeletePermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: MCPServerDeleteNotFoundResponseSerializer,
        },
    )
    def delete(self, request: Request, mcpserver_id: str) -> Response:
        """Delete an existing MCP server.

        This method deletes an existing MCP server. Only the user who created the MCP server can delete it.

        Args:
            request (Request): The HTTP request object.
            mcpserver_id (str): The ID of the MCP server to delete.

        Returns:
            Response: The HTTP response object.

        Raises:
            NotFound: If the MCP server doesn't exist.
            PermissionDenied: If the user isn't the creator of the MCP server.
        """

        # Get the authenticated user
        user = request.user

        try:
            # Try to get the MCP server
            mcpserver = MCPServer.objects.get(id=mcpserver_id)

            # Check if the user is the creator of the MCP server
            if mcpserver.user != user:
                # Return the error response
                return Response(
                    {"error": "You do not have permission to delete this MCP server."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Delete the MCP server
            mcpserver.delete()

            # Return 200 OK with success message
            return Response(
                {"message": "MCP server deleted successfully."},
                status=status.HTTP_200_OK,
            )

        except MCPServer.DoesNotExist:
            # If the MCP server doesn't exist, return a 404 error
            return Response(
                {"error": "MCP server not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
