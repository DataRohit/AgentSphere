# Third-party imports
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# Local application imports
from apps.common.renderers import GenericJSONRenderer
from apps.organization.models import Organization
from apps.organization.serializers import (
    OrganizationAuthErrorResponseSerializer,
    OrganizationMembersListResponseSerializer,
    OrganizationNotFoundResponseSerializer,
    OrganizationNotOwnerResponseSerializer,
)
from apps.users.serializers import UserDetailSerializer

# Get the User model
User = get_user_model()


# Organization Members List View
class OrganizationMembersListView(APIView):
    """Organization members list view.

    This view allows organization owners to list all members of their organization.

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
    object_label = "members"

    # Define the schema
    @extend_schema(
        tags=["Organizations"],
        summary="List members of an organization.",
        description="""
        Lists all members of an organization.
        The authenticated user must be the owner of the organization.
        """,
        responses={
            status.HTTP_200_OK: OrganizationMembersListResponseSerializer,
            status.HTTP_403_FORBIDDEN: OrganizationNotOwnerResponseSerializer,
            status.HTTP_404_NOT_FOUND: OrganizationNotFoundResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def get(self, request: Request, organization_id: str) -> Response:
        """List members of an organization.

        This method retrieves all members of an organization.
        The authenticated user must be the owner of the organization.

        Args:
            request (Request): The HTTP request object.
            organization_id (str): The ID of the organization.

        Returns:
            Response: The HTTP response object containing the list of members.
        """

        # Get the organization or return 404
        organization = get_object_or_404(Organization, id=organization_id)

        # Check if the authenticated user is the owner
        if organization.owner != request.user:
            # Return 403 Forbidden with an error message
            return Response(
                {"error": "You are not the owner of this organization."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get all members of the organization
        members = organization.members.all()

        # Serialize the members for the response body
        response_serializer = UserDetailSerializer(members, many=True)

        # Return 200 OK with the serialized members data
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )
