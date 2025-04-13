# Third-party imports
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError

# Project imports
from apps.common.renderers import GenericJSONRenderer

# Import send_templated_mail at the top of the file
from apps.common.utils import send_templated_mail
from apps.organization.models import Organization, OrganizationOwnershipTransfer
from apps.organization.serializers import (
    OrganizationAuthErrorResponseSerializer,
    OrganizationOwnershipTransferNotFoundResponseSerializer,
    OrganizationOwnershipTransferStatusErrorResponseSerializer,
    OrganizationOwnershipTransferStatusSuccessResponseSerializer,
)


# Organization Ownership Transfer Cancel View
class OrganizationOwnershipTransferCancelView(APIView):
    """Organization ownership transfer cancel view.

    This view allows the current owner to cancel an ownership transfer.

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
    object_label = "organization"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the organization ownership transfer cancel view.

        This method handles exceptions for the organization ownership transfer cancel view.

        Args:
            exc: The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return custom format for authentication errors
        if isinstance(exc, (AuthenticationFailed, TokenError)):
            # Return 401 Unauthorized if the authentication failed
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
        summary="Cancel organization ownership transfer.",
        description="""
        Cancels an ownership transfer for an organization.
        Only the current owner can cancel the transfer.
        The transfer must be active (not expired, not already accepted, not rejected, not cancelled).
        """,
        responses={
            status.HTTP_200_OK: OrganizationOwnershipTransferStatusSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: OrganizationOwnershipTransferStatusErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: OrganizationOwnershipTransferNotFoundResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def get(self, request: Request, organization_id: str) -> Response:
        """Cancel organization ownership transfer.

        This method cancels an ownership transfer for an organization.
        Only the current owner can cancel the transfer.

        Args:
            request (Request): The HTTP request object.
            organization_id (str): The ID of the organization.

        Returns:
            Response: The HTTP response object.
        """

        # Try to get the organization by ID
        try:
            # Get the organization
            organization = Organization.objects.get(id=organization_id)

        except Organization.DoesNotExist:
            # Return 404 Not Found if the organization doesn't exist
            return Response(
                {"error": "Organization not found or you don't have permission."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the user is the owner of the organization
        if organization.owner != request.user:
            # Return 404 Not Found if the user is not the owner
            return Response(
                {"error": "Organization not found or you don't have permission."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get the active transfer for this organization
        transfer = OrganizationOwnershipTransfer.get_active_transfer(organization)
        if not transfer:
            # Return 400 Bad Request if there's no active transfer
            return Response(
                {"error": "No active ownership transfer found for this organization."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Cancel the transfer
            transfer.cancel_transfer()

            # Get domain part for the email footer
            domain_part = settings.ACTIVATION_DOMAIN

            # Send notification email to the new owner
            context = {
                "current_owner": transfer.current_owner,
                "new_owner": transfer.new_owner,
                "organization": transfer.organization,
                "domain_part": domain_part,
            }
            send_templated_mail(
                template_name="organization/email/ownership_transfer_cancelled.html",
                subject=f"Ownership Transfer Cancelled for {transfer.organization.name}",
                context=context,
                recipient_list=[transfer.new_owner.email],
            )

            # Return 200 OK with a success message
            return Response(
                {"message": "Ownership transfer cancelled successfully."},
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            # Return 400 Bad Request with the error
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
