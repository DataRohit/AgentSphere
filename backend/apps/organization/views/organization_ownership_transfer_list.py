# Third-party imports
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# Local application imports
from apps.common.renderers import GenericJSONRenderer
from apps.organization.models import Organization, OrganizationOwnershipTransfer
from apps.organization.serializers import (
    OrganizationAuthErrorResponseSerializer,
    OrganizationOwnershipTransferDetailSerializer,
    OrganizationOwnershipTransfersListResponseSerializer,
    OrganizationTransfersNotFoundResponseSerializer,
)


# Organization Ownership Transfers List View
class OrganizationOwnershipTransfersListView(APIView):
    """Organization ownership transfers list view.

    This view allows organization owners to list all ownership transfers for their organization.

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
    object_label = "transfers"

    # Define the schema
    @extend_schema(
        tags=["Organizations"],
        summary="List ownership transfers for an organization.",
        description="""
        Lists all ownership transfers for an organization.
        The authenticated user must be the owner of the organization.
        """,
        responses={
            status.HTTP_200_OK: OrganizationOwnershipTransfersListResponseSerializer,
            status.HTTP_404_NOT_FOUND: OrganizationTransfersNotFoundResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def get(self, request: Request, organization_id: str) -> Response:
        """List ownership transfers for an organization.

        This method retrieves all ownership transfers for an organization.
        The authenticated user must be the owner of the organization.

        Args:
            request (Request): The HTTP request object.
            organization_id (str): The ID of the organization.

        Returns:
            Response: The HTTP response object containing the list of transfers.
        """

        try:
            # Get the organization
            organization = Organization.objects.get(id=organization_id)

        # If the organization doesn't exist
        except Organization.DoesNotExist:
            # Return 404 Not Found if the organization doesn't exist
            return Response(
                {"error": "Organization not found or you don't have permission to view its transfers."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the authenticated user is the owner
        if organization.owner != request.user:
            # Return 404 Not Found if the user is not the owner
            return Response(
                {"error": "Organization not found or you don't have permission to view its transfers."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get all transfers for the organization
        transfers = OrganizationOwnershipTransfer.objects.filter(organization=organization)

        # Serialize the transfers for the response body
        response_serializer = OrganizationOwnershipTransferDetailSerializer(transfers, many=True)

        # Return 200 OK with the serialized transfers data
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


# User Received Ownership Transfers List View
class UserReceivedOwnershipTransfersListView(APIView):
    """User received ownership transfers list view.

    This view allows users to list all ownership transfers where they are the intended new owner.

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
    object_label = "transfers"

    # Define the schema
    @extend_schema(
        tags=["Organizations"],
        summary="List ownership transfers where the authenticated user is the intended new owner.",
        description="""
        Lists all ownership transfers where the authenticated user is the intended new owner.
        """,
        responses={
            status.HTTP_200_OK: OrganizationOwnershipTransfersListResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        """List ownership transfers where the authenticated user is the intended new owner.

        This method retrieves all ownership transfers where the authenticated user is the intended new owner.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object containing the list of transfers.
        """

        # Get all transfers where the authenticated user is the intended new owner
        transfers = OrganizationOwnershipTransfer.objects.filter(new_owner=request.user)

        # Serialize the transfers for the response body
        response_serializer = OrganizationOwnershipTransferDetailSerializer(transfers, many=True)

        # Return 200 OK with the serialized transfers data
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )
