# Third-party imports
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# Local application imports
from apps.common.renderers import GenericJSONRenderer
from apps.tools.models import MCPServer
from apps.tools.serializers import (
    MCPServerAuthErrorResponseSerializer,
    MCPServerCreateErrorResponseSerializer,
    MCPServerCreateSerializer,
    MCPServerCreateSuccessResponseSerializer,
    MCPServerSerializer,
)

# Get the User model
User = get_user_model()


# MCPServer creation view
class MCPServerCreateView(APIView):
    """MCPServer creation view.

    This view allows authenticated users to create new MCP servers within an organization.
    The user must be a member of the organization to create MCP servers within it.

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

    # Define the schema for the POST view
    @extend_schema(
        tags=["MCP Servers"],
        summary="Create a new MCP server in the specified organization.",
        description=f"""
        Creates a new MCP server within the specified organization with the authenticated user as the creator.
        The user must be a member of the specified organization.
        A user can create a maximum of {MCPServer.MAX_MCPSERVERS_PER_USER_PER_ORGANIZATION} MCP servers per organization.
        """,  # noqa: E501
        request=MCPServerCreateSerializer,
        responses={
            status.HTTP_201_CREATED: MCPServerCreateSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: MCPServerCreateErrorResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: MCPServerAuthErrorResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        """Create a new MCP server in the specified organization.

        This method creates a new MCP server within the specified organization with the
        authenticated user as the creator. The organization ID is specified in the request body.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Create a new MCP server instance
        serializer = MCPServerCreateSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        # Validate the serializer
        if serializer.is_valid():
            # Save the MCP server instance
            mcpserver = serializer.save()

            # Serialize the created MCP server for the response body
            response_serializer = MCPServerSerializer(mcpserver)

            # Return 201 Created with the serialized MCP server data directly
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED,
            )

        # Return 400 Bad Request with the serializer errors
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
