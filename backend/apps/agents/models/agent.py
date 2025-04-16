# Standard library imports
from urllib.parse import quote

# Third-party imports
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
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
    system prompt, and visibility settings. A user can create a maximum of 5 agents
    per organization.

    Attributes:
        name (CharField): The name of the AI agent.
        description (TextField): A detailed description of the agent.
        system_prompt (TextField): The system prompt used to define agent behavior.
        organization (ForeignKey): The organization this agent belongs to.
        user (ForeignKey): The user who created this agent.
        llm (ForeignKey): The LLM model this agent is connected to.
        is_public (BooleanField): Whether this agent is publicly visible to other users in the organization.
        avatar_url (URLField): URL for the agent's avatar image.

    Meta:
        verbose_name (str): Human-readable name for the model.
        verbose_name_plural (str): Human-readable plural name for the model.
        ordering (list): Default ordering for model instances.
        db_table (str): The database table name.
    """

    # Maximum number of agents a user can create per organization
    MAX_AGENTS_PER_USER_PER_ORGANIZATION = 5

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

    # LLM model connected to this agent
    llm = models.ForeignKey(
        "llms.LLM",
        verbose_name=_("LLM Model"),
        on_delete=models.CASCADE,
        related_name="agents",
        help_text=_("The LLM model this agent uses for responses"),
        null=True,
        blank=True,
    )

    # Agent visibility setting
    is_public = models.BooleanField(
        verbose_name=_("Public"),
        default=False,
        help_text=_("Whether this agent is publicly visible to other users in the organization"),
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
        base_url = f"{settings.DICEBEAR_SERVICE_URL}/9.x/avataaars/png"

        # Encode the agent's name
        encoded_name = quote(self.name)

        # Generate the avatar URL parameters
        params = (
            f"seed={encoded_name}&eyes=happy,wink&facialHair[]&facialHairProbability=0&mouth=smile&eyebrows=default"
        )

        # Return the complete avatar URL
        return f"{base_url}?{params}"

    # Custom clean method to validate organization and user consistency
    def clean(self):
        """Validate that agent and LLM belong to the same organization and user.

        Ensures that the agent and its associated LLM model belong to the
        same organization and were created by the same user.

        Raises:
            ValidationError: If the organization or user doesn't match.
        """

        # Call the parent clean method
        super().clean()

        # Check if both agent and LLM have been assigned
        if self.llm:
            # Validate organization consistency
            if self.organization and self.llm.organization and self.organization != self.llm.organization:
                # Raise a validation error
                raise ValidationError(
                    {
                        "llm": _(
                            "The agent and LLM must belong to the same organization.",
                        ),
                    },
                )

            # Validate user consistency
            if self.user and self.llm.user and self.user != self.llm.user:
                # Raise a validation error
                raise ValidationError(
                    {"llm": _("The agent and LLM must be created by the same user.")},
                )

            # If agent has organization but LLM doesn't, assign agent's organization to LLM
            if self.organization and not self.llm.organization:
                # Assign the organization to the LLM
                self.llm.organization = self.organization

                # Save the LLM
                self.llm.save(update_fields=["organization"])

            # If agent has user but LLM doesn't, assign agent's user to LLM
            if self.user and not self.llm.user:
                # Assign the user to the LLM
                self.llm.user = self.user

                # Save the LLM
                self.llm.save(update_fields=["user"])
