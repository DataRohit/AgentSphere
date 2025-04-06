# Standard library imports
from urllib.parse import quote

from django.contrib.auth import get_user_model

# Third-party imports
from django.db import models
from django.utils.translation import gettext_lazy as _

# Local application imports
from apps.common.models.timestamped import TimeStampedModel
from apps.organization.models import Organization

# Get the User model
User = get_user_model()


# Agent model
class Agent(TimeStampedModel):
    """Model for AI agents in the system.

    This model stores AI agent information including name, description,
    system prompt, and visibility settings.

    Attributes:
        name (CharField): The name of the AI agent.
        description (TextField): A detailed description of the agent.
        system_prompt (TextField): The system prompt used to define agent behavior.
        is_public (BooleanField): Whether the agent is publicly visible.
        organization (ForeignKey): The organization this agent belongs to.
        user (ForeignKey): The user who created this agent.
        avatar_url (URLField): URL for the agent's avatar image.

    Meta:
        verbose_name (str): Human-readable name for the model.
        verbose_name_plural (str): Human-readable plural name for the model.
        ordering (list): Default ordering for model instances.
        db_table (str): The database table name.
    """

    # Agent name
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
    )

    # Agent description
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
    )

    # Agent system prompt
    system_prompt = models.TextField(
        verbose_name=_("System Prompt"),
    )

    # Agent visibility
    is_public = models.BooleanField(
        verbose_name=_("Is Public"),
        default=False,
        help_text=_("Whether this agent is publicly visible"),
    )

    # Organization the agent belongs to
    organization = models.ForeignKey(
        Organization,
        verbose_name=_("Organization"),
        on_delete=models.CASCADE,
        related_name="agents",
        null=True,
        blank=True,
    )

    # User who created the agent
    user = models.ForeignKey(
        User,
        verbose_name=_("Created By"),
        on_delete=models.CASCADE,
        related_name="created_agents",
        null=True,
        blank=True,
    )

    # Meta class for Agent model configuration
    class Meta:
        """Meta class for Agent model configuration.

        Attributes:
            verbose_name (str): Human-readable name for the model.
            verbose_name_plural (str): Human-readable plural name for the model.
            ordering (list): Default ordering for model instances.
            db_table (str): The database table name.
        """

        # Human-readable model name
        verbose_name = _("Agent")

        # Human-readable plural model name
        verbose_name_plural = _("Agents")

        # Default ordering by name
        ordering = ["name"]

        # Specify the database table name
        db_table = "agents_agent"

    # String representation of the agent
    def __str__(self) -> str:
        """Return a string representation of the agent.

        Returns:
            str: The name of the agent.
        """

        # Return the name of the agent
        return self.name

    # Generate and return the DiceBear avatar URL for this agent
    def avatar_url(self) -> str:
        """Generate and return the DiceBear avatar URL for this agent.

        The URL uses the agent's name as the seed for consistent avatar generation.

        Returns:
            str: The complete avatar URL.
        """

        # Generate the avatar URL
        base_url = "https://api.dicebear.com/9.x/avataaars/png"

        # Encode the agent's name
        encoded_name = quote(self.name)

        # Generate the avatar URL parameters
        params = (
            f"seed={encoded_name}&eyes=happy,wink&facialHair[]&"
            f"facialHairProbability=0&mouth=smile&eyebrows=default"
        )

        # Return the complete avatar URL
        return f"{base_url}?{params}"
