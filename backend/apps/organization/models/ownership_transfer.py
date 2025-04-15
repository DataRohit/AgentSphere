# Third-party imports
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Local application imports
from apps.common.models import TimeStampedModel
from apps.organization.models.organization import Organization

# Get the User model
User = get_user_model()


# Organization Ownership Transfer model
class OrganizationOwnershipTransfer(TimeStampedModel):
    """Organization Ownership Transfer model.

    This model tracks ownership transfer requests for organizations. Only the current owner
    of an organization can initiate a transfer, and the new owner must be a member of the
    same organization. The process includes initializing, accepting, rejecting, canceling,
    and cleanup of transfer records.

    Attributes:
        organization (ForeignKey): The organization for which ownership is being transferred.
        current_owner (ForeignKey): The current owner of the organization.
        new_owner (ForeignKey): The proposed new owner of the organization.
        expiration_time (DateTimeField): When the transfer request expires.
        is_accepted (BooleanField): Whether the transfer has been accepted.
        is_rejected (BooleanField): Whether the transfer has been rejected.
        is_expired (BooleanField): Whether the transfer request has expired.
        is_cancelled (BooleanField): Whether the transfer has been cancelled.

    Meta:
        verbose_name (str): Human-readable name for the model.
        verbose_name_plural (str): Human-readable plural name for the model.
        ordering (list): Default ordering for model instances.
        db_table (str): The database table name.
        unique_together (tuple): Fields that together must be unique.
    """

    # Default expiration time for transfer requests (72 hours)
    DEFAULT_EXPIRATION_HOURS = 72

    # Organization being transferred
    organization = models.ForeignKey(
        Organization,
        verbose_name=_("Organization"),
        on_delete=models.CASCADE,
        related_name="ownership_transfers",
    )

    # Current owner of the organization
    current_owner = models.ForeignKey(
        User,
        verbose_name=_("Current Owner"),
        on_delete=models.CASCADE,
        related_name="initiated_ownership_transfers",
    )

    # New owner of the organization
    new_owner = models.ForeignKey(
        User,
        verbose_name=_("New Owner"),
        on_delete=models.CASCADE,
        related_name="received_ownership_transfers",
    )

    # Expiration time for the transfer request
    expiration_time = models.DateTimeField(
        verbose_name=_("Expiration Time"),
    )

    # Transfer status flags
    is_accepted = models.BooleanField(
        verbose_name=_("Accepted Status"),
        default=False,
    )

    # Rejected status
    is_rejected = models.BooleanField(
        verbose_name=_("Rejected Status"),
        default=False,
    )

    # Expired status
    is_expired = models.BooleanField(
        verbose_name=_("Expired Status"),
        default=False,
    )

    # Cancelled status
    is_cancelled = models.BooleanField(
        verbose_name=_("Cancelled Status"),
        default=False,
    )

    # Meta class for OrganizationOwnershipTransfer model configuration
    class Meta:
        """Meta class for OrganizationOwnershipTransfer model configuration.

        Attributes:
            verbose_name (str): Human-readable name for the model.
            verbose_name_plural (str): Human-readable plural name for the model.
            ordering (list): Default ordering for model instances.
            db_table (str): The database table name.
        """

        # Human-readable model name
        verbose_name = _("Organization Ownership Transfer")

        # Human-readable plural model name
        verbose_name_plural = _("Organization Ownership Transfers")

        # Default ordering by creation date
        ordering = ["-created_at"]

        # Specify the database table name
        db_table = "organization_ownership_transfer"

    # String representation of the transfer
    def __str__(self) -> str:
        """Return a string representation of the ownership transfer.

        Returns:
            str: A string representation of the ownership transfer.
        """

        # Return the string representation of the ownership transfer
        return f"Transfer of {self.organization.name} from {self.current_owner} to {self.new_owner}"

    # Check if the transfer request is currently active
    @property
    def is_active(self) -> bool:
        """Check if the transfer request is currently active.

        An active transfer request is one that hasn't been accepted, rejected,
        cancelled, or expired.

        Returns:
            bool: True if the transfer is active, False otherwise.
        """

        # Return True if the transfer is active, False otherwise
        return not (self.is_accepted or self.is_rejected or self.is_cancelled or self.is_expired)

    # Get the active transfer request for an organization, if any
    @classmethod
    def get_active_transfer(cls, organization: Organization):
        """Get the active transfer request for an organization, if any.

        Args:
            organization (Organization): The organization to check.

        Returns:
            OrganizationOwnershipTransfer: The active transfer request, or None if none exists.
        """

        try:
            # Return the active transfer request
            return cls.objects.get(
                organization=organization,
                is_accepted=False,
                is_rejected=False,
                is_cancelled=False,
                is_expired=False,
                expiration_time__gt=timezone.now(),
            )

        # If no active transfer request exists
        except cls.DoesNotExist:
            # Return None
            return None

    # Get an expired transfer request for an organization, if any
    @classmethod
    def get_expired_transfer(
        cls,
        organization: Organization,
    ):
        """Get an expired transfer request for an organization, if any.

        This method finds a transfer request that has expired but hasn't been
        marked as expired yet.

        Args:
            organization (Organization): The organization to check.

        Returns:
            OrganizationOwnershipTransfer: The expired transfer request, or None if none exists.
        """

        try:
            # Return the expired transfer request
            return cls.objects.get(
                organization=organization,
                is_accepted=False,
                is_rejected=False,
                is_cancelled=False,
                is_expired=False,
                expiration_time__lte=timezone.now(),
            )

        # If no expired transfer request exists
        except cls.DoesNotExist:
            # Return None
            return None

    # Clean up all expired transfer requests
    @classmethod
    def cleanup_expired_transfers(cls):
        """Clean up all expired transfer requests.

        This method deletes all transfer requests that have expired.
        It can be run as a scheduled task.
        """

        # Get current time
        now = timezone.now()

        # Delete all expired transfers
        cls.objects.filter(
            is_accepted=False,
            is_rejected=False,
            is_cancelled=False,
            is_expired=False,
            expiration_time__lte=now,
        ).delete()

    # Mark the transfer request as expired
    def mark_as_expired(self) -> None:
        """Mark the transfer request as expired.

        Deletes this transfer record since it's expired.
        """

        # Instead of marking as expired, just delete the record
        self.delete()

    # Accept the ownership transfer
    def accept_transfer(self) -> None:
        """Accept the ownership transfer.

        Updates the organization's ownership and then deletes this transfer record.
        """

        # If the transfer request is not active
        if not self.is_active:
            # Error message
            error_message = "Cannot accept an inactive transfer request."

            # Raise a ValueError
            raise ValueError(error_message) from None

        # Update the organization's owner
        self.organization.owner = self.new_owner
        self.organization.save()

        # Delete this transfer record
        self.delete()

    # Reject the ownership transfer
    def reject_transfer(self) -> None:
        """Reject the ownership transfer.

        Deletes this transfer record.
        """

        # If the transfer request is not active
        if not self.is_active:
            # Error message
            error_message = "Cannot reject an inactive transfer request."

            # Raise a ValueError
            raise ValueError(error_message) from None

        # Delete this transfer record
        self.delete()

    # Cancel the ownership transfer
    def cancel_transfer(self) -> None:
        """Cancel the ownership transfer.

        Deletes this transfer record.
        """

        # If the transfer request is not active
        if not self.is_active:
            # Error message
            error_message = "Cannot cancel an inactive transfer request."

            # Raise a ValueError
            raise ValueError(error_message) from None

        # Delete this transfer record
        self.delete()
