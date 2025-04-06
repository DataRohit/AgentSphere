# Third-party imports
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

# Project imports
from apps.common.models import TimeStampedModel

# Get the User model
User = get_user_model()


# Organization model
class Organization(TimeStampedModel):
    """Organization model for the application.

    This model stores information about organizations that users can create and join.
    One user can create a maximum of 3 organizations, and each organization has an
    owner and members.

    Attributes:
        name (CharField): The name of the organization.
        description (TextField): A description of the organization.
        website (URLField): The website URL of the organization.
        logo (ImageField): The logo image of the organization.
        owner (ForeignKey): The user who created and owns the organization.
        members (ManyToManyField): Users who are members of the organization.
        is_active (BooleanField): Flag indicating if the organization is active.

    Meta:
        verbose_name (str): Human-readable name for the model.
        verbose_name_plural (str): Human-readable plural name for the model.
        ordering (list): Default ordering for model instances.
        db_table (str): The database table name.
    """

    # Maximum number of organizations a user can create
    MAX_ORGANIZATIONS_PER_USER = 3

    # Organization name field
    name = models.CharField(
        verbose_name=_("Organization Name"),
        max_length=100,
    )

    # Organization description field
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
    )

    # Organization website field
    website = models.URLField(
        verbose_name=_("Website"),
        blank=True,
    )

    # Organization logo field
    logo = models.ImageField(
        verbose_name=_("Logo"),
        upload_to="organization_logos/",
        blank=True,
        null=True,
    )

    # Owner of the organization
    owner = models.ForeignKey(
        User,
        verbose_name=_("Owner"),
        on_delete=models.CASCADE,
        related_name="owned_organizations",
    )

    # Members of the organization
    members = models.ManyToManyField(
        User,
        verbose_name=_("Members"),
        related_name="organizations",
        blank=True,
    )

    # Organization active status
    is_active = models.BooleanField(
        verbose_name=_("Active Status"),
        default=True,
    )

    # Meta class for Organization model configuration
    class Meta:
        """Meta class for Organization model configuration.

        Attributes:
            verbose_name (str): Human-readable name for the model.
            verbose_name_plural (str): Human-readable plural name for the model.
            ordering (list): Default ordering for model instances.
            db_table (str): The database table name.
            unique_together (tuple): Fields that together must be unique.
        """

        # Human-readable model name
        verbose_name = _("Organization")

        # Human-readable plural model name
        verbose_name_plural = _("Organizations")

        # Default ordering by creation date
        ordering = ["-created_at"]

        # Specify the database table name
        db_table = "organization_organization"

        # Ensure a user cannot create multiple organizations with the same name
        unique_together = ("owner", "name")

    # String representation of the organization
    def __str__(self) -> str:
        """Return a string representation of the organization.

        Returns:
            str: The name of the organization.
        """

        # Return the organization name
        return self.name

    # Add a member to the organization
    def add_member(self, user: User) -> None:
        """Add a user as a member of the organization.

        Args:
            user (User): The user to add as a member.
        """

        # If the user is not already a member
        if user not in self.members.all():
            # Add the user to the organization
            self.members.add(user)

    # Remove a member from the organization
    def remove_member(self, user: User) -> None:
        """Remove a user from the organization's members.

        Args:
            user (User): The user to remove from members.
        """

        # If the user is a member
        if user in self.members.all():
            # Remove the user from the organization
            self.members.remove(user)

    # Get the number of members in the organization
    @property
    def member_count(self) -> int:
        """Get the number of members in the organization.

        Returns:
            int: The count of members in the organization.
        """

        # Return the number of members
        return self.members.count()

    # Get the logo URL for the organization
    @property
    def logo_url(self) -> str:
        """Get the logo URL for the organization.

        If no logo has been uploaded, generate one using DiceBear API.

        Returns:
            str: URL to the organization's logo.
        """

        # If the organization has a logo
        if self.logo and hasattr(self.logo, "url"):
            # Return the logo URL
            return self.logo.url

        # Generate a logo using DiceBear API with organization name as seed
        seed = slugify(self.name)

        # Return the logo URL
        return f"https://api.dicebear.com/9.x/shapes/svg?seed={seed}"


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

    is_rejected = models.BooleanField(
        verbose_name=_("Rejected Status"),
        default=False,
    )

    is_expired = models.BooleanField(
        verbose_name=_("Expired Status"),
        default=False,
    )

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
        return not (
            self.is_accepted or self.is_rejected or self.is_cancelled or self.is_expired
        )

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
