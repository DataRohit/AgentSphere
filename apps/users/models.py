# Third-party imports
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
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


# User activation token model
class UserActivationToken(TimeStampedModel):
    """User activation token model.

    This model stores the token and UID used for user account activation.
    Tokens are valid for a limited time (default: 30 minutes) and are deleted
    after successful activation.

    Attributes:
        user (ForeignKey): The user associated with this activation token.
        uid (CharField): The base64-encoded user ID used in the activation link.
        token (CharField): The token used for verification in the activation link.
        expires_at (DateTimeField): When this activation token expires.

    Meta:
        verbose_name (str): Human-readable name for the model.
        verbose_name_plural (str): Human-readable plural name for the model.
        ordering (list): Default ordering for model instances.
        unique_together (tuple): Fields that together must be unique.
        db_table (str): The database table name.
    """

    # Define the expiration time in minutes
    EXPIRATION_MINUTES = 30

    # User association
    user = models.ForeignKey(
        "users.User",
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="activation_tokens",
    )

    # UID field for the activation link
    uid = models.CharField(
        verbose_name=_("User ID"),
        max_length=255,
    )

    # Token field for the activation link
    token = models.CharField(
        verbose_name=_("Activation Token"),
        max_length=255,
    )

    # Expiration timestamp
    expires_at = models.DateTimeField(
        verbose_name=_("Expires At"),
    )

    # Meta class for UserActivationToken model configuration
    class Meta:
        """Meta class for UserActivationToken model configuration.

        Attributes:
            verbose_name (str): Human-readable name for the model.
            verbose_name_plural (str): Human-readable plural name for the model.
            ordering (list): Default ordering for model instances.
            unique_together (tuple): Fields that together must be unique.
            db_table (str): The database table name.
        """

        # Human-readable model name
        verbose_name = _("User Activation Token")

        # Human-readable plural model name
        verbose_name_plural = _("User Activation Tokens")

        # Default ordering by creation date
        ordering = ["-created_at"]

        # Ensure uid and token combination is unique
        unique_together = ("uid", "token")

        # Specify the database table name
        db_table = "users_user_activation_token"

    # Override save method to set expiration date if not already set
    def save(self, *args, **kwargs):
        """Override save method to set expiration date if not already set.

        This method ensures that the expiration date is set if not already set.
        """

        # Set expiration date if not already set
        if not self.expires_at:
            # Set expiration date
            self.expires_at = timezone.now() + timedelta(
                minutes=self.EXPIRATION_MINUTES,
            )

        # Call super save method
        super().save(*args, **kwargs)

    # Check if the token has expired
    @property
    def is_expired(self) -> bool:
        """Check if the token has expired.

        Returns:
            bool: True if the token has expired, False otherwise.
        """

        # Return True if the token has expired
        return timezone.now() > self.expires_at


# User deletion token model
class UserDeletionToken(TimeStampedModel):
    """User deletion token model.

    This model stores the token and UID used for user account deletion.
    Tokens are valid for a limited time (default: 30 minutes) and are deleted
    after successful deletion.

    Attributes:
        user (ForeignKey): The user associated with this deletion token.
        uid (CharField): The base64-encoded user ID used in the deletion link.
        token (CharField): The token used for verification in the deletion link.
        expires_at (DateTimeField): When this deletion token expires.

    Meta:
        verbose_name (str): Human-readable name for the model.
        verbose_name_plural (str): Human-readable plural name for the model.
        ordering (list): Default ordering for model instances.
        unique_together (tuple): Fields that together must be unique.
        db_table (str): The database table name.
    """

    # Define the expiration time in minutes
    EXPIRATION_MINUTES = 30

    # User association
    user = models.ForeignKey(
        "users.User",
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="deletion_tokens",
    )

    # UID field for the deletion link
    uid = models.CharField(
        verbose_name=_("User ID"),
        max_length=255,
    )

    # Token field for the deletion link
    token = models.CharField(
        verbose_name=_("Deletion Token"),
        max_length=255,
    )

    # Expiration timestamp
    expires_at = models.DateTimeField(
        verbose_name=_("Expires At"),
    )

    # Meta class for UserDeletionToken model configuration
    class Meta:
        """Meta class for UserDeletionToken model configuration.

        Attributes:
            verbose_name (str): Human-readable name for the model.
            verbose_name_plural (str): Human-readable plural name for the model.
            ordering (list): Default ordering for model instances.
            unique_together (tuple): Fields that together must be unique.
            db_table (str): The database table name.
        """

        # Human-readable model name
        verbose_name = _("User Deletion Token")

        # Human-readable plural model name
        verbose_name_plural = _("User Deletion Tokens")

        # Default ordering by creation date
        ordering = ["-created_at"]

        # Ensure uid and token combination is unique
        unique_together = ("uid", "token")

        # Specify the database table name
        db_table = "users_user_deletion_token"

    # Override save method to set expiration date if not already set
    def save(self, *args, **kwargs):
        """Override save method to set expiration date if not already set.

        This method ensures that the expiration date is set if not already set.
        """

        # Set expiration date if not already set
        if not self.expires_at:
            # Set expiration date
            self.expires_at = timezone.now() + timedelta(
                minutes=self.EXPIRATION_MINUTES,
            )

        # Call super save method
        super().save(*args, **kwargs)

    # Check if the token has expired
    @property
    def is_expired(self) -> bool:
        """Check if the token has expired.

        Returns:
            bool: True if the token has expired, False otherwise.
        """

        # Return True if the token has expired
        return timezone.now() > self.expires_at
