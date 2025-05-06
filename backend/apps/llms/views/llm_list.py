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
from apps.llms.models import LLM
from apps.llms.serializers import (
    LLMAuthErrorResponseSerializer,
    LLMListMissingParamResponseSerializer,
    LLMListNotFoundResponseSerializer,
    LLMListResponseSerializer,
    LLMSerializer,
)
from apps.organization.models import Organization

# Get the User model
User = get_user_model()


# LLM list view
class LLMListView(APIView):
    """LLM list view.

    This view allows organization owners to list LLM configurations within their organization.
    It requires the organization_id and user_id parameters. Only the organization owner can
    view LLMs created by other members of the organization.

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
    object_label = "llms"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the LLM list view.

        This method handles exceptions for the LLM list view.

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
        tags=["LLMs"],
        summary="List LLM configurations within an organization by user ID.",
        description="""
        Lists LLM configurations within the specified organization for a specific user.
        Only the organization owner can view LLMs created by other members.
        Both organization_id and user_id parameters are mandatory.
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
                description="User ID to filter LLMs by creator (required)",
                required=True,
                type=str,
            ),
        ],
        responses={
            status.HTTP_200_OK: LLMListResponseSerializer,
            status.HTTP_400_BAD_REQUEST: LLMListMissingParamResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: LLMAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: LLMAuthErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: LLMListNotFoundResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:  # noqa: PLR0911
        """List LLM configurations within an organization by user ID.

        This method lists LLM configurations within the specified organization for a specific user.
        Only the organization owner can view LLMs created by other members.
        Both organization_id and user_id parameters are mandatory.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object with the list of LLM configurations.
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

        # Check if user_id is provided
        user_id = request.query_params.get("user_id")
        if not user_id:
            # Return 400 Bad Request if user_id is not provided
            return Response(
                {"error": "Missing required parameter: user_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Get the organization
            organization = Organization.objects.get(id=organization_id)

        except Organization.DoesNotExist:
            # Return 404 Not Found if the organization doesn't exist
            return Response(
                {"error": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the user is a member of the specified organization
        if not user.organizations.filter(id=organization_id).exists():
            # Return 404 Not Found if the user is not a member of the organization
            return Response(
                {"error": "No LLM configurations found matching the criteria."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the user is trying to view LLMs created by another user
        if user.id != user_id:
            # Only the organization owner can view LLMs created by other members
            if organization.owner != user:
                # Return 403 Forbidden if the user is not the organization owner
                return Response(
                    {"error": "Only the organization owner can view LLMs created by other members."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        try:
            # Check if the target user exists
            User.objects.get(id=user_id)

            # Check if the user is a member of the organization
            if not organization.members.filter(id=user_id).exists():
                # Return 404 Not Found if the target user is not a member of the organization
                return Response(
                    {"error": "The specified user is not a member of this organization."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        except User.DoesNotExist:
            # Return 404 Not Found if the user doesn't exist
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get LLMs created by the specified user in the organization
        queryset = LLM.objects.filter(organization_id=organization_id, user_id=user_id)

        # Check if any LLM configurations were found
        if not queryset.exists():
            # Return 404 Not Found if no LLMs match the criteria
            return Response(
                {"error": "No LLM configurations found matching the criteria."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Serialize the LLM configurations
        serializer = LLMSerializer(queryset, many=True)

        # Return the serialized LLM configurations directly
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
