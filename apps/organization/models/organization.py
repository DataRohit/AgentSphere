# Third-party imports
from django.contrib.auth import get_user_model
from django.db import models
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
        return f"https://api.dicebear.com/9.x/shapes/png?seed={seed}"
