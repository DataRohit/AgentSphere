# Third-party imports
from django.contrib.auth import get_user_model
from django.db.models import Q
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
    MCPServerListMissingParamResponseSerializer,
    MCPServerListNotFoundResponseSerializer,
    MCPServerListResponseSerializer,
    MCPServerSerializer,
)

# Get the User model
User = get_user_model()


# MCPServer list view
class MCPServerListView(APIView):
    """MCPServer list view.

    This view allows authenticated users to list all MCP servers within an organization.
    It requires the organization_id parameter and returns all MCP servers in that organization,
    including those created by other members of the organization.
    It supports filtering by tags.

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
    def handle_exception(self, exc):
        """Handle exceptions for the MCPServer list view.

        This method handles exceptions for the MCPServer list view.

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

    # Define the schema for the list view
    @extend_schema(
        tags=["MCP Servers"],
        summary="List all MCP servers within an organization.",
        description="""
        Lists all MCP servers within the specified organization, including those created by
        other members of the organization. The organization_id parameter is mandatory.
        Supports filtering by tags.
        Returns 400 if organization_id is not provided.
        Returns 404 if no MCP servers are found matching the criteria.
        """,
        parameters=[
            OpenApiParameter(
                name="organization_id",
                description="Organization ID (required)",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="tags",
                description="Filter by comma-separated tags",
                required=False,
                type=str,
            ),
        ],
        responses={
            status.HTTP_200_OK: MCPServerListResponseSerializer,
            status.HTTP_400_BAD_REQUEST: MCPServerListMissingParamResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: MCPServerAuthErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: MCPServerListNotFoundResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        """List all MCP servers within an organization.

        This method lists all MCP servers within the specified organization,
        including those created by other members of the organization.
        The organization_id parameter is mandatory.

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
                # Return 403 Forbidden if the user is not a member of the organization
                return Response(
                    {"error": "You are not a member of this organization."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Get all MCP servers in the specified organization
            queryset = MCPServer.objects.filter(organization=organization)

        except Organization.DoesNotExist:
            # Return 404 Not Found if the organization doesn't exist
            return Response(
                {"error": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Apply tags filter if provided
        tags = request.query_params.get("tags")
        if tags:
            # Split the tags string by comma and filter by any of the tags
            tag_list = [tag.strip() for tag in tags.split(",")]

            # Initialize the tag query
            tag_query = Q()

            # Traverse the tag list
            for tag in tag_list:
                # Build the tag query
                tag_query |= Q(tags__icontains=tag)

            # Filter the queryset by the tag query
            queryset = queryset.filter(tag_query)

        # Check if any MCP servers were found
        if not queryset.exists():
            # Return 404 Not Found if no MCP servers match the criteria
            return Response(
                {"error": "No MCP servers found matching the criteria."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Serialize the MCP servers
        serializer = MCPServerSerializer(queryset, many=True)

        # Return the serialized MCP servers directly
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
