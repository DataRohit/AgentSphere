# Third-party imports
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

# Local application imports
from apps.common.models import TimeStampedModel
from apps.organization.models import Organization

# Get the User model
User = get_user_model()


# GroupChat model
class GroupChat(TimeStampedModel):
    """Model for group chats between a user and multiple agents.

    This model represents a conversation where a single user can interact with
    multiple agents in the same chat. It tracks the user and maintains a many-to-many
    relationship with agents.

    Attributes:
        title (CharField): The title of the group chat.
        organization (ForeignKey): The organization this chat belongs to.
        user (ForeignKey): The user participating in this chat.
        agents (ManyToManyField): The agents participating in this group chat.
        is_public (BooleanField): Whether this chat is publicly visible to other users in the organization.
        summary (TextField): A summary of the chat conversation.

    Meta:
        verbose_name (str): Human-readable name for the model.
        verbose_name_plural (str): Human-readable plural name for the model.
        ordering (list): Default ordering for model instances.
        db_table (str): The database table name.
    """

    # Chat title
    title = models.CharField(
        verbose_name=_("Title"),
        max_length=255,
    )

    # Organization the chat belongs to
    organization = models.ForeignKey(
        Organization,
        verbose_name=_("Organization"),
        on_delete=models.CASCADE,
        related_name="group_chats",
    )

    # User participating in the chat
    user = models.ForeignKey(
        User,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="group_chats",
    )

    # Agents participating in the group chat
    agents = models.ManyToManyField(
        "agents.Agent",
        verbose_name=_("Agents"),
        related_name="group_chats",
        help_text=_("The agents participating in this group chat"),
    )

    # Chat visibility setting
    is_public = models.BooleanField(
        verbose_name=_("Public"),
        default=False,
        help_text=_("Whether this chat is publicly visible to other users in the organization"),
    )

    # Chat summary
    summary = models.TextField(
        verbose_name=_("Summary"),
        blank=True,
        default="",
        help_text=_("A summary of the chat conversation"),
    )

    # Meta class for GroupChat model configuration
    class Meta:
        """Meta class for GroupChat model configuration.

        Attributes:
            verbose_name (str): Human-readable name for the model.
            verbose_name_plural (str): Human-readable plural name for the model.
            ordering (list): Default ordering for model instances.
            db_table (str): The database table name.
        """

        # Human-readable model name
        verbose_name = _("Group Chat")

        # Human-readable plural model name
        verbose_name_plural = _("Group Chats")

        # Default ordering by creation date (newest first)
        ordering = ["-created_at"]

        # Specify the database table name
        db_table = "chats_group_chat"

    # String representation of the group chat
    def __str__(self) -> str:
        """Return a string representation of the group chat.

        Returns:
            str: The title of the chat.
        """

        # Return the title of the chat
        return self.title
