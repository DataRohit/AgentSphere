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
from apps.chats.models import GroupChat
from apps.chats.serializers import GroupChatSerializer
from apps.chats.serializers.group_chats_list import (
    GroupChatsListAuthErrorResponseSerializer,
    GroupChatsListMissingParamResponseSerializer,
    GroupChatsListNotFoundResponseSerializer,
    GroupChatsListPermissionDeniedResponseSerializer,
    GroupChatsListSuccessResponseSerializer,
)
from apps.common.renderers import GenericJSONRenderer
from apps.organization.models import Organization

# Get the User model
User = get_user_model()


# Group chats list view
class GroupChatsListView(APIView):
    """Group chats list view.

    This view allows authenticated users to list group chats within an organization.
    It requires the organization_id parameter and returns chats based on user permissions:
    - Organization owners can see all group chats in the organization
    - Organization members can see their own group chats and public group chats in the organization

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
    def handle_exception(self, exc):
        """Handle exceptions for the group chats list view.

        This method handles exceptions for the group chats list view.

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

    # Define the schema for the GET view
    @extend_schema(
        tags=["Group Chats"],
        summary="List group chats within an organization.",
        description="""
        Lists group chats within the specified organization based on user permissions:
        - Organization owners can see all group chats in the organization
        - Organization members can see their own group chats and public group chats in the organization
        The organization_id parameter is mandatory.
        Additional filters for user_id and is_public are available.
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
                name="is_public",
                description="Filter by public status (true/false)",
                required=False,
                type=bool,
            ),
        ],
        responses={
            status.HTTP_200_OK: GroupChatsListSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: GroupChatsListMissingParamResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: GroupChatsListAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: GroupChatsListPermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: GroupChatsListNotFoundResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        """List group chats within an organization.

        This method lists group chats within the specified organization based on user permissions:
        - Organization owners can see all group chats in the organization
        - Organization members can see their own group chats and public group chats in the organization
        The organization_id parameter is mandatory.

        Additional filters can be applied using query parameters:
        - user_id: Filter chats by specific user
        - is_public: Filter chats by public status (true/false)

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object with the list of group chats.
        """

        # Get the authenticated user
        user = request.user

        # Get the organization_id from the query parameters
        organization_id = request.query_params.get("organization_id")

        # Check if organization_id is provided
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
                # Organization owner can see all group chats
                queryset = GroupChat.objects.filter(organization=organization)

            else:
                # Organization member can see their own group chats and public group chats
                queryset = GroupChat.objects.filter(
                    Q(organization=organization) & (Q(user=user) | Q(is_public=True)),
                )

            # If user_id is provided
            user_id = request.query_params.get("user_id")
            if user_id:
                # Filter by user_id
                queryset = queryset.filter(user_id=user_id)

            # If is_public is provided
            is_public = request.query_params.get("is_public")
            if is_public is not None:
                # Convert string to boolean
                is_public_bool = is_public.lower() == "true"

                # Filter by is_public
                queryset = queryset.filter(is_public=is_public_bool)

            # Check if any group chats were found
            if not queryset.exists():
                # Return 404 Not Found if no group chats were found
                return Response(
                    {"error": "No group chats found matching the criteria."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Serialize the group chats
            serializer = GroupChatSerializer(queryset, many=True)

            # Return 200 OK with the serialized group chats
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        except Organization.DoesNotExist:
            # Return 404 Not Found if the organization does not exist
            return Response(
                {"error": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
