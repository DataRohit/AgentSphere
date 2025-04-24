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
from apps.chats.models import SingleChat
from apps.chats.serializers import SingleChatSerializer
from apps.chats.serializers.single_chats_list import (
    SingleChatsListAuthErrorResponseSerializer,
    SingleChatsListMissingParamResponseSerializer,
    SingleChatsListNotFoundResponseSerializer,
    SingleChatsListPermissionDeniedResponseSerializer,
    SingleChatsListSuccessResponseSerializer,
)
from apps.common.renderers import GenericJSONRenderer
from apps.organization.models import Organization

# Get the User model
User = get_user_model()


# Single chats list view
class SingleChatsListView(APIView):
    """Single chats list view.

    This view allows authenticated users to list chats within an organization.
    It requires the organization_id parameter and returns chats based on user permissions:
    - Organization owners can see all chats in the organization
    - Organization members can see their own chats and public chats in the organization

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
    object_label = "chats"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the single chats list view.

        This method handles exceptions for the single chats list view.

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

    # Define the schema for the GET view
    @extend_schema(
        tags=["Single Chats"],
        summary="List chats within an organization.",
        description="""
        Lists chats within the specified organization based on user permissions:
        - Organization owners can see all chats in the organization
        - Organization members can see their own chats and public chats in the organization
        The organization_id parameter is mandatory.
        Additional filters for user_id, agent_id, and is_public are available.
        """,
        parameters=[
            OpenApiParameter(
                name="organization_id",
                description="Organization ID (required)",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="user_id",
                description="Filter by user ID",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="agent_id",
                description="Filter by agent ID",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="is_public",
                description="Filter by public status (true/false)",
                required=False,
                type=bool,
            ),
        ],
        responses={
            status.HTTP_200_OK: SingleChatsListSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: SingleChatsListMissingParamResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: SingleChatsListAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: SingleChatsListPermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: SingleChatsListNotFoundResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        """List chats within an organization.

        This method lists chats within the specified organization based on user permissions:
        - Organization owners can see all chats in the organization
        - Organization members can see their own chats and public chats in the organization
        The organization_id parameter is mandatory.

        Additional filters can be applied using query parameters:
        - user_id: Filter chats by specific user
        - agent_id: Filter chats by specific agent
        - is_public: Filter chats by public status (true/false)

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object with the list of chats.
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

            # Initialize queryset based on user's role in the organization
            if user == organization.owner:
                # Organization owner can see all chats
                queryset = SingleChat.objects.filter(organization=organization)

            else:
                # Organization member can see their own chats and public chats
                queryset = SingleChat.objects.filter(
                    Q(organization=organization) & (Q(user=user) | Q(is_public=True)),
                )

            # If user_id is provided
            user_id = request.query_params.get("user_id")
            if user_id:
                # Filter by user_id
                queryset = queryset.filter(user_id=user_id)

            # If agent_id is provided
            agent_id = request.query_params.get("agent_id")
            if agent_id:
                # Filter by agent_id
                queryset = queryset.filter(agent_id=agent_id)

            # If is_public is provided
            is_public = request.query_params.get("is_public")
            if is_public is not None:
                # Convert string to boolean
                is_public_bool = is_public.lower() == "true"

                # Filter by is_public
                queryset = queryset.filter(is_public=is_public_bool)

            # Check if any chats were found
            if not queryset.exists():
                # Return 404 Not Found if no chats match the criteria
                return Response(
                    {"error": "No chats found matching the criteria."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Serialize the chats
            serializer = SingleChatSerializer(queryset, many=True)

            # Return the serialized chats
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        except Organization.DoesNotExist:
            # Return 404 Not Found if the organization doesn't exist
            return Response(
                {"error": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
