# Third-party imports
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedModel


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
