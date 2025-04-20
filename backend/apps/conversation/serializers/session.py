# Third-party imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

# Local application imports
from apps.chats.serializers import GroupChatSerializer, SingleChatSerializer
from apps.conversation.models import Session


# LLM nested serializer for Session responses
class SessionLLMSerializer(serializers.Serializer):
    """LLM serializer for use in Session responses.

    Attributes:
        id (UUID): LLM's unique identifier.
        api_type (str): The API provider type.
        model (str): The specific model name.
        api_type_display (str): Human-readable display name for the API type.
    """

    # ID field
    id = serializers.UUIDField(
        help_text=_("Unique identifier for the LLM."),
        read_only=True,
    )

    # API type field
    api_type = serializers.CharField(
        help_text=_("API provider type code."),
        read_only=True,
    )

    # Model field
    model = serializers.CharField(
        help_text=_("Specific model name for the selected API type."),
        read_only=True,
    )

    # API type display field
    api_type_display = serializers.CharField(
        help_text=_("Human-readable display name for the API type."),
        read_only=True,
    )


# Session response schema
class SessionResponseSchema(serializers.ModelSerializer):
    """Response schema for the Session model.

    This serializer is used for the response schema in Swagger documentation.
    It includes the session details and the WebSocket URL.

    Attributes:
        id (UUIDField): The ID of the session.
        single_chat (SingleChatSerializer): The serialized single chat (if applicable).
        group_chat (GroupChatSerializer): The serialized group chat (if applicable).
        is_active (BooleanField): Whether the session is active.
        selector_prompt (CharField): Prompt used for selecting the appropriate agent or tool.
        llm (SessionLLMSerializer): The LLM model used for this session (if applicable).
        websocket_url (CharField): The WebSocket URL for the session.
        created_at (DateTimeField): When the session was created.
        updated_at (DateTimeField): When the session was last updated.
    """

    # Serializers for single chat
    single_chat = SingleChatSerializer(read_only=True)

    # Serializer for group chat
    group_chat = GroupChatSerializer(read_only=True)

    # LLM details
    llm = serializers.SerializerMethodField(
        help_text=_("LLM model used for this session."),
    )

    # WebSocket URL field
    websocket_url = serializers.CharField(
        help_text=_("The WebSocket URL for the session."),
        read_only=True,
    )

    # Get LLM details
    @extend_schema_field(SessionLLMSerializer())
    def get_llm(self, obj: Session) -> dict | None:
        """Get LLM details for the session.

        Args:
            obj (Session): The session instance.

        Returns:
            dict | None: The LLM details including id, api_type, model, and api_type_display.
        """

        # If the session has an LLM
        if obj.llm:
            # Return the LLM details
            return {
                "id": str(obj.llm.id),
                "api_type": obj.llm.api_type,
                "model": obj.llm.model,
                "api_type_display": obj.llm.get_api_type_display(),
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
        selector_prompt (CharField): Prompt used for selecting the appropriate agent or tool.
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
