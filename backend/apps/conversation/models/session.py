# Third-party imports
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

# Local application imports
from apps.chats.models import GroupChat, SingleChat
from apps.common.models import TimeStampedModel


# Session model
class Session(TimeStampedModel):
    """Model for conversation sessions in the system.

    This model represents a conversation session that can be linked to either
    a single chat or a group chat, but not both simultaneously. It tracks whether
    the session is currently active.

    Attributes:
        single_chat (ForeignKey): The single chat this session is linked to (optional).
        group_chat (ForeignKey): The group chat this session is linked to (optional).
        is_active (BooleanField): Whether this session is currently active.

    Meta:
        verbose_name (str): Human-readable name for the model.
        verbose_name_plural (str): Human-readable plural name for the model.
        ordering (list): Default ordering for model instances.
        db_table (str): The database table name.
    """

    # Single chat relationship (optional)
    single_chat = models.ForeignKey(
        SingleChat,
        verbose_name=_("Single Chat"),
        on_delete=models.CASCADE,
        related_name="sessions",
        null=True,
        blank=True,
    )

    # Group chat relationship (optional)
    group_chat = models.ForeignKey(
        GroupChat,
        verbose_name=_("Group Chat"),
        on_delete=models.CASCADE,
        related_name="sessions",
        null=True,
        blank=True,
    )

    # Session active status
    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
        help_text=_("Whether this session is currently active"),
    )

    # Meta class for Session model configuration
    class Meta:
        """Meta class for Session model configuration.

        Attributes:
            verbose_name (str): Human-readable name for the model.
            verbose_name_plural (str): Human-readable plural name for the model.
            ordering (list): Default ordering for model instances.
            db_table (str): The database table name.
        """

        # Human-readable model name
        verbose_name = _("Session")

        # Human-readable plural model name
        verbose_name_plural = _("Sessions")

        # Default ordering by creation date (newest first)
        ordering = ["-created_at"]

        # Specify the database table name
        db_table = "conversation_session"

    # String representation of the Session model
    def __str__(self) -> str:
        """Return a string representation of the session.

        Returns:
            str: A string representation of the session.
        """

        # If the session is linked to a single chat
        if self.single_chat:
            # Return the single chat title
            return f"Session for Single Chat: {self.single_chat.title}"

        # If the session is linked to a group chat
        if self.group_chat:
            # Return the group chat title
            return f"Session for Group Chat: {self.group_chat.title}"

        # If the session is not linked to a single chat or group chat
        return f"Session {self.id}"

    # Clean method to validate that only one of single_chat or group_chat is provided
    def clean(self) -> None:
        """Validate that only one of single_chat or group_chat is provided.

        Raises:
            ValidationError: If both single_chat and group_chat are provided or neither is provided.
        """

        # Check if both single_chat and group_chat are provided
        if self.single_chat and self.group_chat:
            # Raise a validation error if both single_chat and group_chat are provided
            raise ValidationError(
                _("A session cannot be linked to both a single chat and a group chat simultaneously."),
            )

        # Check if neither single_chat nor group_chat is provided
        if not self.single_chat and not self.group_chat:
            # Raise a validation error if neither single_chat nor group_chat is provided
            raise ValidationError(_("A session must be linked to either a single chat or a group chat."))

    # Save method to ensure validation is performed
    def save(self, *args, **kwargs) -> None:
        """Save the session instance.

        Performs validation before saving to ensure that only one of
        single_chat or group_chat is provided.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """

        # Perform validation
        self.clean()

        # Call the parent save method
        super().save(*args, **kwargs)
