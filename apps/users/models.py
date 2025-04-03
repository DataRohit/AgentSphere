# Standard library imports
import uuid

# Third-party imports
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

# Project imports
from apps.users.managers import UserManager
from apps.users.validators import UsernameValidator


# Custom user model extending Django's AbstractUser
class User(AbstractUser):
    """Custom user model for the application.

    This model extends Django's AbstractUser to provide custom user functionality.
    It uses email-based authentication and includes additional fields for user management.

    Attributes:
        id (UUIDField): Primary key and unique identifier for the user.
        first_name (CharField): User's first name.
        last_name (CharField): User's last name.
        email (EmailField): User's email address, used for authentication.
        username (CharField): User's username, must be unique.

    Properties:
        full_name (str): Concatenated first and last name of the user.

    Meta:
        verbose_name (str): Human-readable name for the model.
        verbose_name_plural (str): Human-readable plural name for the model.
        ordering (list): Default ordering for model instances.
    """

    # UUID field for unique identification and primary key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

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

    # Field used for email-based authentication
    EMAIL_FIELD = "email"

    # Field used for username-based authentication
    USERNAME_FIELD = "email"

    # Required fields for user creation
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    # Custom user manager instance
    objects = UserManager()

    class Meta:
        """Meta class for User model configuration.

        Attributes:
            verbose_name (str): Human-readable name for the model.
            verbose_name_plural (str): Human-readable plural name for the model.
            ordering (list): Default ordering for model instances.
        """

        # Human-readable model name
        verbose_name = _("User")

        # Human-readable plural model name
        verbose_name_plural = _("Users")

        # Default ordering by date joined
        ordering = ["-date_joined"]

    @property
    def full_name(self) -> str:
        """Get the user's full name.

        Returns:
            str: Concatenated first and last name of the user.
        """
        # Combine first and last name
        full_name = f"{self.first_name} {self.last_name}"

        # Return trimmed full name
        return full_name.strip()
