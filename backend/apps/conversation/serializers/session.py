# Third-party imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

# Local application imports
from apps.conversation.models import Session


# Agent nested serializer for Session responses
class SessionAgentSerializer(serializers.Serializer):
    """Agent serializer for use in Session responses.

    Attributes:
        id (UUID): Agent's unique identifier.
        name (str): Name of the agent.
        description (str): Description of the agent.
        avatar_url (str): URL for the agent's avatar image.
    """

    # ID field
    id = serializers.UUIDField(
        help_text=_("Unique identifier for the agent."),
        read_only=True,
    )

    # Name field
    name = serializers.CharField(
        help_text=_("Name of the agent."),
        read_only=True,
    )

    # Description field
    description = serializers.CharField(
        help_text=_("Description of the agent."),
        read_only=True,
    )

    # Avatar URL field
    avatar_url = serializers.URLField(
        help_text=_("URL for the agent's avatar image."),
        read_only=True,
    )


# SingleChat nested serializer for Session responses
class SessionSingleChatSerializer(serializers.Serializer):
    """SingleChat serializer for use in Session responses.

    Attributes:
        id (UUID): SingleChat's unique identifier.
        title (str): Title of the chat.
        agent (SessionAgentSerializer): Agent associated with the chat, including avatar URL.
    """

    # ID field
    id = serializers.UUIDField(
        help_text=_("Unique identifier for the chat."),
        read_only=True,
    )

    # Title field
    title = serializers.CharField(
        help_text=_("Title of the chat."),
        read_only=True,
    )

    # Agent field
    agent = SessionAgentSerializer(
        help_text=_("Agent associated with the chat."),
        read_only=True,
    )


# GroupChat nested serializer for Session responses
class SessionGroupChatSerializer(serializers.Serializer):
    """GroupChat serializer for use in Session responses.

    Attributes:
        id (UUID): GroupChat's unique identifier.
        title (str): Title of the chat.
        agents (list): List of agents associated with the chat, each including avatar URL.
    """

    # ID field
    id = serializers.UUIDField(
        help_text=_("Unique identifier for the chat."),
        read_only=True,
    )

    # Title field
    title = serializers.CharField(
        help_text=_("Title of the chat."),
        read_only=True,
    )

    # Agents field
    agents = serializers.ListField(
        child=SessionAgentSerializer(),
        help_text=_("Agents associated with the chat."),
        read_only=True,
    )


# LLM nested serializer for Session responses
class SessionLLMSerializer(serializers.Serializer):
    """LLM serializer for use in Session responses.

    Attributes:
        id (UUID): LLM's unique identifier.
        base_url (str): The base URL for the LLM API.
        model (str): The specific model name.
    """

    # ID field
    id = serializers.UUIDField(
        help_text=_("Unique identifier for the LLM."),
        read_only=True,
    )

    # Base URL field
    base_url = serializers.URLField(
        help_text=_("Base URL for the LLM API."),
        read_only=True,
    )

    # Model field
    model = serializers.CharField(
        help_text=_("Specific model name for the selected API type."),
        read_only=True,
    )


# Session response schema
class SessionResponseSchema(serializers.ModelSerializer):
    """Response schema for the Session model.

    This serializer is used for the response schema in Swagger documentation.
    It includes the session details and the WebSocket URL.

    Attributes:
        id (UUIDField): The ID of the session.
        single_chat (SingleChatSerializer): The serialized single chat with agent avatar URL (if applicable).
        group_chat (GroupChatSerializer): The serialized group chat with agent avatar URLs (if applicable).
        is_active (BooleanField): Whether the session is active.
        selector_prompt (TextField): Prompt used for selecting the appropriate agent or tool.
        llm (SessionLLMSerializer): The LLM model used for this session (if applicable).
        websocket_url (CharField): The WebSocket URL for the session.
        created_at (DateTimeField): When the session was created.
        updated_at (DateTimeField): When the session was last updated.
    """

    # Single chat details
    single_chat = serializers.SerializerMethodField(
        help_text=_("Single chat associated with this session."),
    )

    # Group chat details
    group_chat = serializers.SerializerMethodField(
        help_text=_("Group chat associated with this session."),
    )

    # LLM details
    llm = serializers.SerializerMethodField(
        help_text=_("LLM model used for this session."),
    )

    # WebSocket URL field
    websocket_url = serializers.CharField(
        help_text=_("The WebSocket URL for the session."),
        read_only=True,
    )

    # Get single chat details
    @extend_schema_field(SessionSingleChatSerializer())
    def get_single_chat(self, obj: Session) -> dict | None:
        """Get single chat details for the session.

        Args:
            obj (Session): The session instance.

        Returns:
            dict | None: The single chat details including id, title, and agent with avatar URL.
        """

        # If the session has a single chat
        if obj.single_chat:
            # Prepare the response
            result = {
                "id": str(obj.single_chat.id),
                "title": obj.single_chat.title,
            }

            # Add agent details if available
            if obj.single_chat.agent:
                result["agent"] = {
                    "id": str(obj.single_chat.agent.id),
                    "name": obj.single_chat.agent.name,
                    "description": obj.single_chat.agent.description,
                    "avatar_url": obj.single_chat.agent.avatar_url(),
                }

            # If the single chat has no agent
            else:
                # Set the agent to None
                result["agent"] = None

            # Return the result
            return result

        # Return None if the session has no single chat
        return None

    # Get group chat details
    @extend_schema_field(SessionGroupChatSerializer())
    def get_group_chat(self, obj: Session) -> dict | None:
        """Get group chat details for the session.

        Args:
            obj (Session): The session instance.

        Returns:
            dict | None: The group chat details including id, title, and agents with avatar URLs.
        """

        # If the session has a group chat
        if obj.group_chat:
            # Get the agents
            agents = []

            # If the group chat has agents
            if obj.group_chat.agents.exists():
                # Prepare the agents
                agents = [
                    {
                        "id": str(agent.id),
                        "name": agent.name,
                        "description": agent.description,
                        "avatar_url": agent.avatar_url(),
                    }
                    for agent in obj.group_chat.agents.all()
                ]

            # Return the group chat details
            return {
                "id": str(obj.group_chat.id),
                "title": obj.group_chat.title,
                "agents": agents,
            }

        # Return None if the session has no group chat
        return None

    # Get LLM details
    @extend_schema_field(SessionLLMSerializer())
    def get_llm(self, obj: Session) -> dict | None:
        """Get LLM details for the session.

        Args:
            obj (Session): The session instance.

        Returns:
            dict | None: The LLM details including id, base_url, and model.
        """

        # If the session has an LLM
        if obj.llm:
            # Return the LLM details
            return {
                "id": str(obj.llm.id),
                "base_url": obj.llm.base_url,
                "model": obj.llm.model,
            }

        # Return None if the session has no LLM
        return None

    # Meta class for SessionResponseSchema configuration
    class Meta:
        """Meta class for SessionResponseSchema configuration.

        Attributes:
            model (Session): The model class.
            fields (list): The fields to include in the serializer.
        """

        # Model to use for the serializer
        model = Session

        # Fields to include in the serializer
        fields = [
            "id",
            "single_chat",
            "group_chat",
            "is_active",
            "selector_prompt",
            "llm",
            "websocket_url",
            "created_at",
            "updated_at",
        ]

        # Read-only fields
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


# Session serializer
class SessionSerializer(serializers.ModelSerializer):
    """Serializer for the Session model.

    This serializer is used for serializing and deserializing Session instances.
    It includes the basic session fields without nested serializers.

    Attributes:
        id (UUIDField): The ID of the session.
        single_chat (ForeignKey): The single chat this session is linked to (optional).
        group_chat (ForeignKey): The group chat this session is linked to (optional).
        is_active (BooleanField): Whether the session is active.
        selector_prompt (TextField): Prompt used for selecting the appropriate agent or tool.
        llm (ForeignKey): The LLM model used for this session (optional).
        created_at (DateTimeField): When the session was created.
        updated_at (DateTimeField): When the session was last updated.
    """

    # Meta class for SessionSerializer configuration
    class Meta:
        """Meta class for SessionSerializer configuration.

        Attributes:
            model (Session): The model class.
            fields (list): The fields to include in the serializer.
        """

        # Model to use for the serializer
        model = Session

        # Fields to include in the serializer
        fields = [
            "id",
            "single_chat",
            "group_chat",
            "is_active",
            "selector_prompt",
            "llm",
            "created_at",
            "updated_at",
        ]

        # Read-only fields
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
