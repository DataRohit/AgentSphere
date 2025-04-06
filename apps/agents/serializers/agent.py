# Third-party imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

# Project imports
from apps.agents.models import Agent


# Agent serializer
class AgentSerializer(serializers.ModelSerializer):
    """Agent serializer.

    This serializer provides a representation of the Agent model.

    Attributes:
        id (UUID): The agent's ID.
        name (str): The agent's name.
        description (str): The agent's description.
        type (str): The agent's type or category.
        system_prompt (str): The agent's system prompt.
        is_public (bool): Whether the agent is publicly visible.
        avatar_url (str): The URL to the agent's avatar.
        organization_id (UUID): The ID of the organization the agent belongs to.
        user_id (UUID): The ID of the user who created the agent.
        created_at (datetime): The date and time the agent was created.
        updated_at (datetime): The date and time the agent was last updated.

    Meta:
        model (Agent): The model class.
        fields (list): The fields to include in the serializer.
        read_only_fields (list): Fields that are read-only.
    """

    # Avatar URL field
    avatar_url = serializers.SerializerMethodField(
        help_text=_("URL to the agent's avatar."),
    )

    # Organization ID field
    organization_id = serializers.UUIDField(
        source="organization.id",
        read_only=True,
        help_text=_("ID of the organization the agent belongs to."),
    )

    # User ID field
    user_id = serializers.UUIDField(
        source="user.id",
        read_only=True,
        help_text=_("ID of the user who created the agent."),
    )

    # Meta class for AgentSerializer configuration
    class Meta:
        """Meta class for AgentSerializer configuration.

        Attributes:
            model (Agent): The model class.
            fields (list): The fields to include in the serializer.
            read_only_fields (list): Fields that are read-only.
        """

        # Model to use for the serializer
        model = Agent

        # Fields to include in the serializer
        fields = [
            "id",
            "name",
            "description",
            "type",
            "system_prompt",
            "is_public",
            "avatar_url",
            "organization_id",
            "user_id",
            "created_at",
            "updated_at",
        ]

        # Read-only fields
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    # Get the avatar URL for the agent
    @extend_schema_field(serializers.URLField())
    def get_avatar_url(self, obj: Agent) -> str:
        """Get the avatar URL for the agent.

        Args:
            obj (Agent): The agent instance.

        Returns:
            str: The URL to the agent's avatar.
        """

        # Call the avatar_url method to get the URL string
        return obj.avatar_url()


# Define explicit agent response schema for Swagger documentation
class AgentResponseSchema(serializers.Serializer):
    """Agent response schema for Swagger documentation.

    Defines the structure of an agent in the response.

    Attributes:
        id (UUID): The agent's ID.
        name (str): The agent's name.
        description (str): The agent's description.
        type (str): The agent's type or category.
        system_prompt (str): The agent's system prompt.
        is_public (bool): Whether the agent is publicly visible.
        avatar_url (str): The URL to the agent's avatar.
        organization_id (UUID): The ID of the organization the agent belongs to.
        user_id (UUID): The ID of the user who created the agent.
        created_at (datetime): The date and time the agent was created.
        updated_at (datetime): The date and time the agent was last updated.
    """

    # ID field
    id = serializers.UUIDField(
        help_text=_("Unique identifier for the agent."),
    )

    # Name field
    name = serializers.CharField(
        help_text=_("Name of the agent."),
    )

    # Description field
    description = serializers.CharField(
        help_text=_("Description of the agent."),
        allow_blank=True,
    )

    # Type field
    type = serializers.CharField(
        help_text=_("Type or category of the agent."),
    )

    # System prompt field
    system_prompt = serializers.CharField(
        help_text=_("System prompt used to define agent behavior."),
    )

    # Is public field
    is_public = serializers.BooleanField(
        help_text=_("Whether the agent is publicly visible."),
    )

    # Avatar URL field
    avatar_url = serializers.URLField(
        help_text=_("URL for the agent's avatar image."),
    )

    # Created at field
    created_at = serializers.DateTimeField(
        help_text=_("Timestamp when the agent was created."),
    )

    # Updated at field
    updated_at = serializers.DateTimeField(
        help_text=_("Timestamp when the agent was last updated."),
    )

    # Organization ID field
    organization_id = serializers.UUIDField(
        help_text=_("ID of the organization the agent belongs to."),
        source="organization.id",
    )

    # User ID field
    user_id = serializers.UUIDField(
        help_text=_("ID of the user who created the agent."),
        source="user.id",
    )
