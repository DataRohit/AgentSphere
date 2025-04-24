# Third-party imports
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

# Local application imports
from apps.common.models import TimeStampedModel

# Get the User model
User = get_user_model()


# Message model
class Message(TimeStampedModel):
    """Model for chat messages in the system.

    This model stores individual messages that can belong to either a SingleChat or a GroupChat.
    Each message is associated with a user or an agent and contains the message content.
    Every message must be associated with a conversation session.

    Attributes:
        single_chat (ForeignKey): The single chat this message belongs to (optional).
        group_chat (ForeignKey): The group chat this message belongs to (optional).
        session (ForeignKey): The conversation session this message belongs to.
        user (ForeignKey): The user who sent this message (if user message).
        agent (ForeignKey): The agent who sent this message (if agent message).
        content (TextField): The content of the message.
        sender (CharField): The sender type of the message (user or agent).

    Meta:
        verbose_name (str): Human-readable name for the model.
        verbose_name_plural (str): Human-readable plural name for the model.
        ordering (list): Default ordering for model instances.
        db_table (str): The database table name.
    """

    # Set the message truncation length
    MESSAGE_TRUNCATION_LENGTH = 30

    # Sender type choices
    class SenderType(models.TextChoices):
        """Sender type choices for the message model.

        Choices:
            USER: Message sent by a user.
            AGENT: Message sent by an agent.
        """

        # User message type
        USER = "user", _("User")

        # Agent message type
        AGENT = "agent", _("Agent")

    # Single chat this message belongs to (optional)
    single_chat = models.ForeignKey(
        "chats.SingleChat",
        verbose_name=_("Single Chat"),
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,
        blank=True,
    )

    # Group chat this message belongs to (optional)
    group_chat = models.ForeignKey(
        "chats.GroupChat",
        verbose_name=_("Group Chat"),
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,
        blank=True,
    )

    # Session this message belongs to
    session = models.ForeignKey(
        "conversation.Session",
        verbose_name=_("Session"),
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,
        blank=True,
    )

    # User who sent the message (if user message)
    user = models.ForeignKey(
        User,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="chat_messages",
        null=True,
        blank=True,
    )

    # Agent who sent the message (if agent message)
    agent = models.ForeignKey(
        "agents.Agent",
        verbose_name=_("Agent"),
        on_delete=models.CASCADE,
        related_name="chat_messages",
        null=True,
        blank=True,
    )

    # Message content
    content = models.TextField(
        verbose_name=_("Content"),
    )

    # Sender type (user or agent)
    sender = models.CharField(
        verbose_name=_("Sender"),
        max_length=10,
        choices=SenderType.choices,
    )

    # Meta class for Message model configuration
    class Meta:
        """Meta class for Message model configuration.

        Attributes:
            verbose_name (str): Human-readable name for the model.
            verbose_name_plural (str): Human-readable plural name for the model.
            ordering (list): Default ordering for model instances.
            db_table (str): The database table name.
        """

        # Human-readable model name
        verbose_name = _("Message")

        # Human-readable plural model name
        verbose_name_plural = _("Messages")

        # Default ordering by creation date (oldest first for conversation flow)
        ordering = ["created_at"]

        # Specify the database table name
        db_table = "chats_message"

    # String representation of the message
    def __str__(self) -> str:
        """Return a string representation of the message.

        Returns:
            str: A short representation of the message with its type and a content preview.
        """

        # Create a short preview of the content
        preview = (
            self.content[: self.MESSAGE_TRUNCATION_LENGTH] + "..."
            if len(self.content) > self.MESSAGE_TRUNCATION_LENGTH
            else self.content
        )

        # Return a string representation with sender type and content preview
        return f"{self.get_sender_display()}: {preview}"

    # Custom clean method to validate chat relationship, session, and sender consistency
    def clean(self):
        """Validate message relationships, session, and sender consistency.

        Ensures that:
        - A message belongs to exactly one chat (either SingleChat or GroupChat)
        - A message is associated with a session
        - The sender type matches the sender field
        - The session is associated with the same chat as the message

        Raises:
            ValidationError: If validation fails for chat, session, or sender relationship.
        """

        # Check if message belongs to exactly one chat
        if (self.single_chat and self.group_chat) or (not self.single_chat and not self.group_chat):
            # Raise a validation error
            raise ValidationError(
                _("Message must belong to exactly one chat (either SingleChat or GroupChat)."),
            )

        # Check if session is set
        if not self.session:
            # Raise a validation error
            raise ValidationError(
                {"session": _("Session must be set for all messages.")},
            )

        # Check session consistency with chat
        if self.single_chat and self.session.single_chat != self.single_chat:
            # Raise a validation error
            raise ValidationError(
                {"session": _("Session must be associated with the same single chat as the message.")},
            )

        # Check session consistency with chat for group chat
        if self.group_chat and self.session.group_chat != self.group_chat:
            # Raise a validation error
            raise ValidationError(
                {"session": _("Session must be associated with the same group chat as the message.")},
            )

        # Check sender consistency for user messages
        if self.sender == self.SenderType.USER and not self.user:
            # Raise a validation error
            raise ValidationError(
                {"user": _("User must be set for user messages.")},
            )

        # Check sender consistency for agent messages
        if self.sender == self.SenderType.AGENT and not self.agent:
            # Raise a validation error
            raise ValidationError(
                {"agent": _("Agent must be set for agent messages.")},
            )
