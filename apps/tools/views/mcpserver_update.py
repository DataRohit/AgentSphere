# Third-party imports
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError

# Project imports
from apps.common.renderers import GenericJSONRenderer
from apps.tools.models import MCPServer
from apps.tools.serializers import (
    MCPServerAuthErrorResponseSerializer,
    MCPServerNotFoundResponseSerializer,
    MCPServerPermissionDeniedResponseSerializer,
    MCPServerSerializer,
    MCPServerUpdateErrorResponseSerializer,
    MCPServerUpdateSerializer,
    MCPServerUpdateSuccessResponseSerializer,
)

# Get the User model
User = get_user_model()


# MCPServer update view
class MCPServerUpdateView(APIView):
    """MCPServer update view.

    This view allows users to update their own MCP servers.
    Only the user who created an MCP server can update it.

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
        """Handle exceptions for the MCPServer update view.

        This method handles exceptions for the MCPServer update view.

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

        # Call the parent method for other exceptions
        return super().handle_exception(exc)

    # Define the schema
    @extend_schema(
        tags=["MCP Servers"],
        summary="Update an existing MCP server.",
        description="""
        Updates an existing MCP server. Only the user who created the MCP server can update it.
        All fields are optional - only the fields that need to be updated should be included.
        """,
        request=MCPServerUpdateSerializer,
        responses={
            status.HTTP_200_OK: MCPServerUpdateSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: MCPServerUpdateErrorResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: MCPServerAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: MCPServerPermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: MCPServerNotFoundResponseSerializer,
        },
    )
    def patch(self, request: Request, mcpserver_id: str) -> Response:
        """Update an existing MCP server.

        This method updates an existing MCP server. Only the user who created the MCP server can update it.

        Args:
            request (Request): The HTTP request object.
            mcpserver_id (str): The ID of the MCP server to update.

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
                    {"error": "You do not have permission to update this MCP server."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Create serializer with the MCP server and data
            serializer = MCPServerUpdateSerializer(
                mcpserver,
                data=request.data,
                partial=True,
            )

            # Validate the serializer
            if serializer.is_valid():
                # Save the updated MCP server
                updated_mcpserver = serializer.save()

                # Serialize the updated MCP server for response
                response_serializer = MCPServerSerializer(updated_mcpserver)

                # Return 200 OK with the updated MCP server data
                return Response(
                    response_serializer.data,
                    status=status.HTTP_200_OK,
                )

            # Return 400 Bad Request with validation errors
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except MCPServer.DoesNotExist:
            # If the MCP server doesn't exist, return a 404 error
            return Response(
                {"error": "MCP server not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
