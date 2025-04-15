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
    OrganizationMembershipListResponseSerializer,
    OrganizationSerializer,
)

# Get the User model
User = get_user_model()


# Organization Member List View
class OrganizationMemberListView(APIView):
    """Organization member list view.

    This view allows authenticated users to list all organizations they are a member of.

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
        """Handle exceptions for the organization member list view.

        This method handles exceptions for the organization member list view.

        Args:
            exc: The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return custom format for authentication errors
        if isinstance(exc, (AuthenticationFailed, TokenError)):
            # Return 401 Unauthorized with the error message
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
        summary="List organizations where user is a member.",
        description="""
        Lists all organizations where the authenticated user is a member.
        This includes organizations the user owns and organizations they have been added to as a member.
        """,
        responses={
            status.HTTP_200_OK: OrganizationMembershipListResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        """List organizations where user is a member.

        This method retrieves all organizations where the authenticated user is a member.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object containing the list of organizations.
        """

        # Get all organizations where the user is a member
        member_organizations = request.user.organizations.all()

        # Get all organizations owned by the user
        owned_organizations = Organization.objects.filter(owner=request.user)

        # Combine the two querysets without duplicates
        organizations = (member_organizations | owned_organizations).distinct()

        # Serialize the organizations for the response body
        response_serializer = OrganizationSerializer(organizations, many=True)

        # Return 200 OK with the serialized organizations data
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )
