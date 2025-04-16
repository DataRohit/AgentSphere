# Third-party imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

# Local application imports
from apps.agents.models import Agent


# Agent organization nested serializer for API documentation
class AgentOrganizationSerializer(serializers.Serializer):
    """Agent organization serializer for use in agent responses.

    Attributes:
        id (UUID): Organization's unique identifier.
        name (str): Name of the organization.
    """

    # ID field
    id = serializers.UUIDField(
        help_text=_("Unique identifier for the organization."),
        read_only=True,
    )

    # Name field
    name = serializers.CharField(
        help_text=_("Name of the organization."),
        read_only=True,
    )


# Agent user nested serializer for API documentation
class AgentUserSerializer(serializers.Serializer):
    """Agent user serializer for use in agent responses.

    Attributes:
        id (UUID): User's unique identifier.
        username (str): Username of the user.
        email (str): Email address of the user.
    """

    # ID field
    id = serializers.UUIDField(
        help_text=_("Unique identifier for the user."),
        read_only=True,
    )

    # Username field
    username = serializers.CharField(
        help_text=_("Username of the user."),
        read_only=True,
    )

    # Email field
    email = serializers.EmailField(
        help_text=_("Email address of the user."),
        read_only=True,
    )


# Agent LLM nested serializer for API documentation
class AgentLLMSerializer(serializers.Serializer):
    """Agent LLM serializer for use in agent responses.

    Attributes:
        id (UUID): LLM's unique identifier.
        api_type (str): Type of API used for this LLM.
        model (str): Model name for this LLM.
    """

    # ID field
    id = serializers.UUIDField(
        help_text=_("Unique identifier for the LLM."),
        read_only=True,
    )

    # API type field
    api_type = serializers.CharField(
        help_text=_("Type of API used for this LLM."),
        read_only=True,
    )

    # Model field
    model = serializers.CharField(
        help_text=_("Model name for this LLM."),
        read_only=True,
    )


# Agent serializer
class AgentSerializer(serializers.ModelSerializer):
    """Agent serializer.

    This serializer provides a representation of the Agent model.

    Attributes:
        id (UUID): The agent's ID.
        name (str): The agent's name.
        description (str): The agent's description.
        system_prompt (str): The agent's system prompt.
        avatar_url (str): The URL to the agent's avatar.
        organization (dict): Organization details including id and name.
        user (dict): User details including id, username, and email.
        llm (dict): LLM details including id, api_type, and model.
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

    # Organization details
    organization = serializers.SerializerMethodField(
        help_text=_("Organization details the agent belongs to."),
    )

    # User details
    user = serializers.SerializerMethodField(
        help_text=_("User details who created the agent."),
    )

    # LLM details
    llm = serializers.SerializerMethodField(
        help_text=_("LLM model details associated with the agent."),
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
            "system_prompt",
            "avatar_url",
            "organization",
            "user",
            "llm",
            "is_public",
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

    # Get organization details
    @extend_schema_field(AgentOrganizationSerializer())
    def get_organization(self, obj: Agent) -> dict:
        """Get organization details for the agent.

        Args:
            obj (Agent): The agent instance.

        Returns:
            dict: The organization details including id and name.
        """

        # If the agent has an organization
        if obj.organization:
            # Return the organization details with string UUID
            return {
                "id": str(obj.organization.id),
                "name": obj.organization.name,
            }

        # Return None if the agent has no organization
        return None

    # Get user details
    @extend_schema_field(AgentUserSerializer())
    def get_user(self, obj: Agent) -> dict:
        """Get user details for the agent.

        Args:
            obj (Agent): The agent instance.

        Returns:
            dict: The user details including id, username, and email.
        """

        # If the agent has a user
        if obj.user:
            # Return the user details with string UUID
            return {
                "id": str(obj.user.id),
                "username": obj.user.username,
                "email": obj.user.email,
            }

        # Return None if the agent has no user
        return None

    # Get LLM details
    @extend_schema_field(AgentLLMSerializer())
    def get_llm(self, obj: Agent) -> dict:
        """Get LLM details for the agent.

        Args:
            obj (Agent): The agent instance.

        Returns:
            dict: The LLM details including id, api_type, and model.
        """

        # If the agent has an LLM
        if obj.llm:
            # Return the LLM details with string UUID
            return {
                "id": str(obj.llm.id),
                "api_type": obj.llm.api_type,
                "model": obj.llm.model,
            }

        # Return None if the agent has no LLM
        return None


# Agent response schema for Swagger documentation
class AgentResponseSchema(serializers.Serializer):
    """Agent response schema for Swagger documentation.

    Defines the structure of an agent in the response.

    Attributes:
        id (UUID): The agent's ID.
        name (str): The agent's name.
        description (str): The agent's description.
        system_prompt (str): The agent's system prompt.
        avatar_url (str): The URL to the agent's avatar.
        is_public (bool): Whether this agent is publicly visible to other users in the organization.
        organization (AgentOrganizationSerializer): Organization details including id and name.
        user (UserSerializer): User details including id, username, and email.
        llm (LLMSerializer): LLM details including id, api_type, and model.
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

    # System prompt field
    system_prompt = serializers.CharField(
        help_text=_("System prompt used to define agent behavior."),
    )

    # Avatar URL field
    avatar_url = serializers.URLField(
        help_text=_("URL for the agent's avatar image."),
    )

    # Is public field
    is_public = serializers.BooleanField(
        help_text=_("Whether this agent is publicly visible to other users in the organization."),
    )

    # Created at field
    created_at = serializers.DateTimeField(
        help_text=_("Timestamp when the agent was created."),
    )

    # Updated at field
    updated_at = serializers.DateTimeField(
        help_text=_("Timestamp when the agent was last updated."),
    )

    # Organization field using the proper serializer
    organization = AgentOrganizationSerializer(
        help_text=_("Organization details the agent belongs to."),
        required=False,
        allow_null=True,
    )

    # User field using the proper serializer
    user = AgentUserSerializer(
        help_text=_("User details who created the agent."),
        required=False,
        allow_null=True,
    )

    # LLM field using the proper serializer
    llm = AgentLLMSerializer(
        help_text=_("LLM model details associated with the agent."),
        required=False,
        allow_null=True,
    )
