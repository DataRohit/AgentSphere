# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer
from apps.organization.models import OrganizationOwnershipTransfer
from apps.users.serializers import UserDetailSerializer


# Organization Ownership Transfer Detail Serializer
class OrganizationOwnershipTransferDetailSerializer(serializers.ModelSerializer):
    """Organization Ownership Transfer Detail Serializer.

    This serializer provides a detailed representation of an organization ownership transfer.

    Attributes:
        id (UUID): The transfer's ID.
        organization_id (UUID): The ID of the organization being transferred.
        organization_name (str): The name of the organization being transferred.
        current_owner (UserDetailSerializer): The current owner of the organization.
        new_owner (UserDetailSerializer): The proposed new owner of the organization.
        expiration_time (datetime): When the transfer request expires.
        is_active (bool): Whether the transfer is currently active.
        created_at (datetime): When the transfer was created.
        updated_at (datetime): When the transfer was last updated.
    """

    # Organization ID field
    organization_id = serializers.UUIDField(
        source="organization.id",
        read_only=True,
        help_text=_("The ID of the organization being transferred."),
    )

    # Organization name field
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
        help_text=_("The name of the organization being transferred."),
    )

    # Current owner field
    current_owner = UserDetailSerializer(read_only=True)

    # New owner field
    new_owner = UserDetailSerializer(read_only=True)

    # Is active field
    is_active = serializers.BooleanField(
        read_only=True,
        help_text=_("Whether the transfer is currently active."),
    )

    # Meta class for OrganizationOwnershipTransferDetailSerializer configuration
    class Meta:
        """Meta class for OrganizationOwnershipTransferDetailSerializer configuration.

        Attributes:
            model (OrganizationOwnershipTransfer): The model class.
            fields (list): The fields to include in the serializer.
            read_only_fields (list): Fields that are read-only.
        """

        # Model to use for the serializer
        model = OrganizationOwnershipTransfer

        # Fields to include in the serializer
        fields = [
            "id",
            "organization_id",
            "organization_name",
            "current_owner",
            "new_owner",
            "expiration_time",
            "is_active",
            "created_at",
            "updated_at",
        ]

        # Read-only fields
        read_only_fields = fields


# Organization Ownership Transfers List Response Serializer
class OrganizationOwnershipTransfersListResponseSerializer(GenericResponseSerializer):
    """Organization Ownership Transfers List Response Serializer.

    This serializer defines the structure of the response for listing organization ownership transfers.
    It includes a status code and a list of transfers.

    Attributes:
        status_code (int): The status code of the response.
        transfers (List[OrganizationOwnershipTransferDetailSerializer]): List of transfer serializers.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code indicating a successful request."),
    )

    # Transfers serializer
    transfers = OrganizationOwnershipTransferDetailSerializer(
        many=True,
        read_only=True,
        help_text=_("List of organization ownership transfers."),
    )


# Organization Not Found Response Serializer
class OrganizationTransfersNotFoundResponseSerializer(GenericResponseSerializer):
    """Organization Transfers Not Found Response Serializer.

    This serializer defines the structure of the response when an organization is not found
    or the user doesn't have permission to view its transfers.

    Attributes:
        status_code (int): The status code of the response.
        error (str): An error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_404_NOT_FOUND,
        read_only=True,
        help_text=_("HTTP status code indicating a not found error."),
    )

    # Error message
    error = serializers.CharField(
        default=_("Organization not found or you don't have permission to view its transfers."),
        read_only=True,
        help_text=_("Error message explaining why the resource was not found."),
    )
