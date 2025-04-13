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
from apps.organization.models import OrganizationOwnershipTransfer
from apps.organization.serializers import (
    OrganizationAuthErrorResponseSerializer,
    OrganizationOwnershipTransferNotFoundResponseSerializer,
    OrganizationOwnershipTransferStatusErrorResponseSerializer,
    OrganizationOwnershipTransferStatusSuccessResponseSerializer,
)


# Organization Ownership Transfer Accept View
class OrganizationOwnershipTransferAcceptView(APIView):
    """Organization ownership transfer accept view.

    This view allows the new owner to accept an ownership transfer.

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
        """Handle exceptions for the organization ownership transfer accept view.

        This method handles exceptions for the organization ownership transfer accept view.

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
        summary="Accept organization ownership transfer.",
        description="""
        Accepts an ownership transfer for an organization.
        Only the new owner can accept the transfer.
        The transfer must be active (not expired, not already accepted, not rejected, not cancelled).
        """,
        responses={
            status.HTTP_200_OK: OrganizationOwnershipTransferStatusSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: OrganizationOwnershipTransferStatusErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: OrganizationOwnershipTransferNotFoundResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def get(self, request: Request, transfer_id: str) -> Response:
        """Accept organization ownership transfer.

        This method accepts an ownership transfer for an organization.
        Only the new owner can accept the transfer.

        Args:
            request (Request): The HTTP request object.
            transfer_id (str): The ID of the transfer.

        Returns:
            Response: The HTTP response object.
        """

        try:
            # Get the transfer
            transfer = OrganizationOwnershipTransfer.objects.get(id=transfer_id)

        except OrganizationOwnershipTransfer.DoesNotExist:
            # Return 404 Not Found if the transfer doesn't exist
            return Response(
                {
                    "error": "Organization ownership transfer not found or you don't have permission.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the user is the new owner
        if transfer.new_owner != request.user:
            # Return 404 Not Found if the user is not the new owner
            return Response(
                {
                    "error": "Organization ownership transfer not found or you don't have permission.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the transfer is active
        if not transfer.is_active:
            # Return 400 Bad Request if the transfer is not active
            return Response(
                {"error": "The ownership transfer is no longer active."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Accept the transfer (this will update the organization's owner)
            transfer.accept_transfer()

            # Get domain part for the email footer
            domain_part = settings.ACTIVATION_DOMAIN

            # Send confirmation emails to both owners
            # Email to previous owner
            previous_owner_context = {
                "previous_owner": transfer.current_owner,
                "new_owner": transfer.new_owner,
                "organization": transfer.organization,
                "domain_part": domain_part,
            }
            send_templated_mail(
                template_name="organization/email/ownership_transfer_accepted_previous_owner.html",
                subject=f"Ownership Transfer Accepted for {transfer.organization.name}",
                context=previous_owner_context,
                recipient_list=[transfer.current_owner.email],
            )

            # Email to new owner
            new_owner_context = {
                "previous_owner": transfer.current_owner,
                "new_owner": transfer.new_owner,
                "organization": transfer.organization,
                "domain_part": domain_part,
            }
            send_templated_mail(
                template_name="organization/email/ownership_transfer_accepted_new_owner.html",
                subject=f"You Are Now the Owner of {transfer.organization.name}",
                context=new_owner_context,
                recipient_list=[transfer.new_owner.email],
            )

            # Return 200 OK with a success message
            return Response(
                {"message": "Ownership transfer accepted successfully."},
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            # Return 400 Bad Request with the error
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
