# Third-party imports
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedModel

# Project imports
from apps.users.managers import UserManager
from apps.users.validators import UsernameValidator


# Custom user model extending Django's AbstractUser
class User(AbstractUser, TimeStampedModel):
    """Custom user model for the application.

    This model extends Django's AbstractUser to provide custom user functionality.
    It uses email-based authentication and includes additional fields for user management.

    Attributes:
        first_name (CharField): User's first name.
        last_name (CharField): User's last name.
        email (EmailField): User's email address, used for authentication.
        username (CharField): User's username, must be unique.
        avatar (ImageField): User's avatar image, uploaded to 'avatars/' directory.

    Properties:
        full_name (str): Concatenated first and last name of the user.

    Meta:
        verbose_name (str): Human-readable name for the model.
        verbose_name_plural (str): Human-readable plural name for the model.
        ordering (list): Default ordering for model instances.
        db_table (str): The database table name.
    """

    # User's first name field
    first_name = models.CharField(verbose_name=_("First Name"), max_length=60)

    # User's last name field
    last_name = models.CharField(verbose_name=_("Last Name"), max_length=60)

    # User's email field for authentication
    email = models.EmailField(
        verbose_name=_("Email Address"),
        unique=True,
        db_index=True,
    )

    # User's username field with validation
    username = models.CharField(
        verbose_name=_("Username"),
        max_length=60,
        unique=True,
        validators=[UsernameValidator],
    )

    # User's avatar field
    avatar = models.ImageField(
        verbose_name=_("Avatar"),
        upload_to="avatars/",
        blank=True,
        null=True,
        help_text=_("User avatar image"),
    )

    # Field used for email-based authentication
    EMAIL_FIELD = "email"

    # Field used for username-based authentication
    USERNAME_FIELD = "email"

    # Required fields for user creation
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    # Custom user manager instance
    objects = UserManager()

    # Meta class for User model configuration
    class Meta:
        """Meta class for User model configuration.

        Attributes:
            verbose_name (str): Human-readable name for the model.
            verbose_name_plural (str): Human-readable plural name for the model.
            ordering (list): Default ordering for model instances.
            db_table (str): The database table name.
        """

        # Human-readable model name
        verbose_name = _("User")

        # Human-readable plural model name
        verbose_name_plural = _("Users")

        # Default ordering by date joined
        ordering = ["-date_joined"]

        # Specify the database table name
        db_table = "users_user"

    # Property for the user's full name
    @property
    def full_name(self) -> str:
        """Get the user's full name.

        Returns:
            str: Concatenated first and last name of the user.
        """

        # Combine first and last name
        full_name = f"{self.first_name} {self.last_name}".title()

        # Return trimmed full name
        return full_name.strip()

    @property
    def avatar_url(self) -> str:
        """Get the user's avatar URL.

        This property returns the URL of the user's avatar.
        If the user has no avatar, it returns the default avatar URL.

        Returns:
            str: The URL of the user's avatar.
        """

        # If the user has an avatar
        if self.avatar and hasattr(self.avatar, "url"):
            # Return the avatar URL
            return self.avatar.url

        # Generate the default avatar URL
        base_url = f"{settings.DICEBEAR_SERVICE_URL}/9.x/avataaars/png"
        params = (
            f"seed={self.username}&eyes=happy,wink&facialHair[]&"
            f"facialHairProbability=0&mouth=smile&eyebrows=default"
        )

        # Return the default avatar URL
        return f"{base_url}?{params}"
