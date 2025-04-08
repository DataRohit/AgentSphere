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

# Project imports
from apps.agents.models import Agent
from apps.agents.serializers import (
    AgentAuthErrorResponseSerializer,
    AgentListNotFoundResponseSerializer,
    AgentListResponseSerializer,
    AgentSerializer,
)
from apps.common.renderers import GenericJSONRenderer

# Get the User model
User = get_user_model()


# Agent list view
class AgentListView(APIView):
    """Agent list view.

    This view allows authenticated users to list all agents they have created (both public
    and private) as well as all public agents from the same organization.
    It supports filtering by organization_id, type, and is_public.

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
    def handle_exception(self, exc):
        """Handle exceptions for the agent list view.

        This method handles exceptions for the agent list view.

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
        tags=["Agents"],
        summary="List agents created by the user and public agents from the same organization.",
        description="""
        Lists all agents created by the authenticated user (both public and private)
        as well as all public agents from the same organization.
        Supports filtering by organization_id, type, and is_public.
        Returns 404 if no agents are found matching the criteria.
        """,
        parameters=[
            OpenApiParameter(
                name="organization_id",
                description="Filter by organization ID",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="type",
                description="Filter by agent type",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="is_public",
                description="Filter by public/private status (true/false)",
                required=False,
                type=bool,
            ),
        ],
        responses={
            status.HTTP_200_OK: AgentListResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: AgentAuthErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: AgentListNotFoundResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        """List agents created by the user and public agents from the same organization.

        This method lists:
        1. All agents created by the authenticated user (both public and private)
        2. All public agents from the same organization(s) as the user

        It supports optional filtering by organization_id, type, and is_public.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object with the list of agents.
        """

        # Get the authenticated user
        user = request.user

        # Get the user's organizations
        user_organizations = user.organizations.all()

        # Build query:
        # - User's agents (both public and private)
        # - Public agents from the user's organizations
        queryset = Agent.objects.filter(
            Q(user=user)  # User's own agents (public or private)
            | Q(
                organization__in=user_organizations,
                is_public=True,
            ),  # Public agents from user's orgs
        ).distinct()

        # Apply organization_id filter if provided
        organization_id = request.query_params.get("organization_id")
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)

        # Apply type filter if provided
        agent_type = request.query_params.get("type")
        if agent_type:
            queryset = queryset.filter(type=agent_type)

        # Apply is_public filter if provided
        is_public = request.query_params.get("is_public")
        if is_public is not None:
            # Convert the string value to boolean
            is_public_bool = is_public.lower() == "true"

            # For is_public=false, only show the user's private agents
            if is_public_bool is False:
                queryset = queryset.filter(user=user, is_public=False)

            # For is_public=true, only show the public agents
            else:
                queryset = queryset.filter(is_public=True)

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
