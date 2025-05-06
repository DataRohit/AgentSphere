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
    LLMListMeResponseSerializer,
    LLMListMissingParamResponseSerializer,
    LLMListNotFoundResponseSerializer,
    LLMSerializer,
)

# Get the User model
User = get_user_model()


# LLM list me view
class LLMListMeView(APIView):
    """LLM list me view.

    This view allows authenticated users to list all LLM configurations they have created.
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
    object_label = "llms"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the LLM list me view.

        This method handles exceptions for the LLM list me view.

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
        tags=["LLMs"],
        summary="List LLM configurations created by the current user.",
        description="""
        Lists all LLM configurations created by the authenticated user.
        Requires organization_id parameter.
        """,
        parameters=[
            OpenApiParameter(
                name="organization_id",
                description="Filter by organization ID (required)",
                required=True,
                type=str,
            ),
        ],
        responses={
            status.HTTP_200_OK: LLMListMeResponseSerializer,
            status.HTTP_400_BAD_REQUEST: LLMListMissingParamResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: LLMAuthErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: LLMListNotFoundResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        """List LLM configurations created by the current user.

        This method lists all LLM configurations created by the authenticated user.
        It requires the organization_id parameter.

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

        # Get the user's organizations
        user_organizations = user.organizations.all()

        # Check if the user is a member of the specified organization
        if not user_organizations.filter(id=organization_id).exists():
            # Return 404 Not Found if the user is not a member of the organization
            return Response(
                {"error": "No LLM configurations found matching the criteria."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Build query for user's LLMs in the specified organization
        queryset = LLM.objects.filter(user=user, organization_id=organization_id)

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
