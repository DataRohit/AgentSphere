# Third-party imports
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
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
from apps.common.utils import send_templated_mail
from apps.organization.models import Organization, OrganizationOwnershipTransfer
from apps.organization.serializers import (
    OrganizationAuthErrorResponseSerializer,
    OrganizationNotFoundResponseSerializer,
    OrganizationOwnershipTransferInitErrorResponseSerializer,
    OrganizationOwnershipTransferInitResponseSerializer,
    OrganizationOwnershipTransferInitSerializer,
)


# Organization Ownership Transfer Initialization View
class OrganizationOwnershipTransferInitView(APIView):
    """Organization ownership transfer initialization view.

    This view allows organization owners to initiate ownership transfers.
    A new owner is specified using the user's ID, email, or username.
    The new owner must be a member of the organization.

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
    object_label = "transfer"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the organization ownership transfer initialization view.

        This method handles exceptions for the organization ownership transfer initialization view.

        Args:
            exc (Exception): The exception that occurred.

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
        summary="Initialize organization ownership transfer.",
        description="""
        Initializes an ownership transfer for an organization.
        Only the current owner can initiate a transfer, and the new owner must be a member of the organization.
        Exactly one identifier (user_id, email, or username) must be provided to identify the new owner.
        The transfer request will expire after 72 hours if not accepted or rejected.
        If an expired transfer request exists, it will be updated.
        """,
        request=OrganizationOwnershipTransferInitSerializer,
        responses={
            status.HTTP_201_CREATED: OrganizationOwnershipTransferInitResponseSerializer,
            status.HTTP_400_BAD_REQUEST: OrganizationOwnershipTransferInitErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: OrganizationNotFoundResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def post(self, request: Request, organization_id: str) -> Response:
        """Initialize organization ownership transfer.

        This method initializes an ownership transfer for an organization.
        Only the current owner can initiate a transfer, and the new owner must be a member of the organization.

        Args:
            request (Request): The HTTP request object.
            organization_id (str): The ID of the organization.

        Returns:
            Response: The HTTP response object.
        """

        try:
            # Get the organization
            organization = Organization.objects.get(id=organization_id)

        except Organization.DoesNotExist:
            # Return 404 Not Found if the organization doesn't exist
            return Response(
                {"error": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the user is the owner of the organization
        if organization.owner != request.user:
            # Return 404 Not Found if the user is not the owner
            return Response(
                {"error": "Organization not found or you don't have permission."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Create the serializer with the organization in the context
        serializer = OrganizationOwnershipTransferInitSerializer(
            data=request.data,
            context={"request": request, "organization": organization},
        )

        # Validate the serializer
        if serializer.is_valid():
            # Get the new owner
            new_owner = serializer.get_user()

            # Check if there's an active transfer for this organization
            active_transfer = OrganizationOwnershipTransfer.get_active_transfer(
                organization,
            )
            if active_transfer:
                # Return an error if there's already an active transfer
                return Response(
                    {
                        "errors": {
                            "non_field_errors": [
                                "There is already an active ownership transfer for this organization.",
                            ],
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if there's an expired transfer that hasn't been marked as expired yet
            expired_transfer = OrganizationOwnershipTransfer.get_expired_transfer(
                organization,
            )
            if expired_transfer:
                # Delete the expired transfer
                expired_transfer.delete()
                expired_transfer = None

            # Calculate the expiration time (72 hours from now)
            expiration_time = timezone.now() + timezone.timedelta(
                hours=OrganizationOwnershipTransfer.DEFAULT_EXPIRATION_HOURS,
            )

            # Create a new transfer request
            transfer = OrganizationOwnershipTransfer.objects.create(
                organization=organization,
                current_owner=request.user,
                new_owner=new_owner,
                expiration_time=expiration_time,
            )

            # Get scheme and domain from settings
            scheme = settings.ACTIVATION_SCHEME
            domain_part = settings.ACTIVATION_DOMAIN

            # Construct full accept URL
            accept_url = f"{scheme}://{domain_part}/organization/transfer/{transfer.id}/accept/"

            # Construct full reject URL
            reject_url = f"{scheme}://{domain_part}/organization/transfer/{transfer.id}/reject/"

            # Send an email to the new owner with accept and reject links
            context = {
                "current_owner": request.user,
                "new_owner": new_owner,
                "organization": organization,
                "transfer_id": transfer.id,
                "expiration_time": transfer.expiration_time,
                "accept_url": accept_url,
                "reject_url": reject_url,
                "domain_part": domain_part,
            }

            # Send the email to the new owner
            send_templated_mail(
                template_name="organization/email/ownership_transfer_request.html",
                subject=f"Ownership Transfer Request for {organization.name}",
                context=context,
                recipient_list=[new_owner.email],
            )

            # Create a cancel URL for the current owner
            relative_cancel_path = reverse(
                "organization:organization-ownership-transfer-cancel",
                kwargs={"organization_id": organization.id},
            )
            cancel_url = f"{scheme}://{domain_part}{relative_cancel_path}"

            # Send a confirmation email to the current owner
            current_owner_context = {
                "current_owner": request.user,
                "new_owner": new_owner,
                "organization": organization,
                "transfer_id": transfer.id,
                "expiration_time": transfer.expiration_time,
                "domain_part": domain_part,
                "cancel_url": cancel_url,
            }

            # Send the email to the current owner
            send_templated_mail(
                template_name="organization/email/ownership_transfer_initiated.html",
                subject=f"You Initiated an Ownership Transfer for {organization.name}",
                context=current_owner_context,
                recipient_list=[request.user.email],
            )

            # Return 201 Created with the transfer data
            return Response(
                {"message": "Transfer initiated successfully."},
                status=status.HTTP_201_CREATED,
            )

        # Return 400 Bad Request with validation errors
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
