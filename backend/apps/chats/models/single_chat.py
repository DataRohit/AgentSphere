# Third-party imports
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

# Local application imports
from apps.common.models import TimeStampedModel
from apps.organization.models import Organization

# Get the User model
User = get_user_model()


# SingleChat model
class SingleChat(TimeStampedModel):
    """Model for one-to-one chats between users and agents.

    This model represents a conversation between a single user and a single agent.
    It contains basic chat information like title and tracks which user and agent
    are involved in the conversation.

    Attributes:
        title (CharField): The title of the chat.
        organization (ForeignKey): The organization this chat belongs to.
        user (ForeignKey): The user participating in this chat.
        agent (ForeignKey): The agent participating in this chat.

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
        related_name="single_chats",
    )

    # User participating in the chat
    user = models.ForeignKey(
        User,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="single_chats",
    )

    # Agent participating in the chat
    agent = models.ForeignKey(
        "agents.Agent",
        verbose_name=_("Agent"),
        on_delete=models.CASCADE,
        related_name="single_chats",
    )

    # Meta class for SingleChat model configuration
    class Meta:
        """Meta class for SingleChat model configuration.

        Attributes:
            verbose_name (str): Human-readable name for the model.
            verbose_name_plural (str): Human-readable plural name for the model.
            ordering (list): Default ordering for model instances.
            db_table (str): The database table name.
        """

        # Human-readable model name
        verbose_name = _("Single Chat")

        # Human-readable plural model name
        verbose_name_plural = _("Single Chats")

        # Default ordering by creation date (newest first)
        ordering = ["-created_at"]

        # Specify the database table name
        db_table = "chats_single_chat"

    # String representation of the single chat
    def __str__(self) -> str:
        """Return a string representation of the single chat.

        Returns:
            str: The title of the chat.
        """

        # Return the title of the chat
        return self.title
