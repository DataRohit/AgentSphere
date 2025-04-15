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

# Local application imports
from apps.common.renderers import GenericJSONRenderer
from apps.organization.models import Organization
from apps.organization.serializers import (
    OrganizationAuthErrorResponseSerializer,
    OrganizationListResponseSerializer,
    OrganizationSerializer,
)

# Get the User model
User = get_user_model()


# Organization List View
class OrganizationListView(APIView):
    """Organization list view.

    This view allows authenticated users to list all organizations they own.

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
    object_label = "organizations"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the organization list view.

        This method handles exceptions for the organization list view.

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

    # Define the schema
    @extend_schema(
        tags=["Organizations"],
        summary="List user's owned organizations.",
        description="""
        Lists all organizations owned by the authenticated user.
        """,
        responses={
            status.HTTP_200_OK: OrganizationListResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        """List user's owned organizations.

        This method retrieves all organizations owned by the authenticated user.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object containing the list of organizations.
        """

        # Get all organizations owned by the user
        organizations = Organization.objects.filter(owner=request.user)

        # Serialize the organizations for the response body
        response_serializer = OrganizationSerializer(organizations, many=True)

        # Return 200 OK with the serialized organizations data
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )
