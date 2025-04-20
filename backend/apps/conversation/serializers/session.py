# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

# Local application imports
from apps.chats.serializers import GroupChatSerializer, SingleChatSerializer
from apps.conversation.models import Session


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
        websocket_url (CharField): The WebSocket URL for the session.
        created_at (DateTimeField): When the session was created.
        updated_at (DateTimeField): When the session was last updated.
    """

    # Serializers for single chat
    single_chat = SingleChatSerializer(read_only=True)

    # Serializer for group chat
    group_chat = GroupChatSerializer(read_only=True)

    # WebSocket URL field
    websocket_url = serializers.CharField(
        help_text=_("The WebSocket URL for the session."),
        read_only=True,
    )

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
            "created_at",
            "updated_at",
        ]

        # Read-only fields
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
