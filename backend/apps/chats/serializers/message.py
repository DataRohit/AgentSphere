# Third-party imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

# Local application imports
from apps.chats.models import Message
from apps.chats.serializers.single_chat import SingleChatAgentSerializer, SingleChatUserSerializer


# Message user nested serializer
class MessageUserSerializer(serializers.Serializer):
    """Message user serializer for use in message responses.

    Attributes:
        id (UUID): User's unique identifier.
        username (str): Username of the user.
        email (str): Email of the user.
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
        help_text=_("Email of the user."),
        read_only=True,
    )


# Message agent nested serializer
class MessageAgentSerializer(serializers.Serializer):
    """Message agent serializer for use in message responses.

    Attributes:
        id (UUID): Agent's unique identifier.
        name (str): Name of the agent.
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


# Message serializer
class MessageSerializer(serializers.ModelSerializer):
    """Serializer for the Message model.

    This serializer provides a representation of a message in a chat,
    including details about the sender (user or agent) and the session it belongs to.

    Attributes:
        id (UUID): The message's ID.
        content (str): The message content.
        sender (str): The sender type (user or agent).
        session (UUID): The ID of the session this message belongs to.
        user (dict): User details if sender is a user.
        agent (dict): Agent details if sender is an agent.
        created_at (datetime): The date and time the message was created.
        updated_at (datetime): The date and time the message was last updated.
    """

    # Session field
    session = serializers.SerializerMethodField(
        help_text=_("ID of the session this message belongs to."),
        read_only=True,
    )

    # User field using the proper serializer
    user = SingleChatUserSerializer(
        help_text=_("User details who sent the message."),
        required=False,
        allow_null=True,
    )

    # Agent field using the proper serializer
    agent = SingleChatAgentSerializer(
        help_text=_("Agent details who sent the message."),
        required=False,
        allow_null=True,
    )

    # Meta class for MessageSerializer configuration
    class Meta:
        """Meta class for MessageSerializer configuration.

        Attributes:
            model (Message): The model class.
            fields (list): The fields to include in the serializer.
            read_only_fields (list): Fields that are read-only.
        """

        # Model to use for the serializer
        model = Message

        # Fields to include in the serializer
        fields = [
            "id",
            "content",
            "sender",
            "session",
            "user",
            "agent",
            "created_at",
            "updated_at",
        ]

        # Read-only fields
        read_only_fields = [
            "id",
            "session",
            "created_at",
            "updated_at",
        ]

    # Get session details
    @extend_schema_field(serializers.UUIDField())
    def get_session(self, obj: Message) -> str:
        """Get session details for the message.

        Args:
            obj (Message): The message instance.

        Returns:
            str: The session ID.
        """

        # Return the session ID with string UUID
        return str(obj.session.id)

    # Get user details
    @extend_schema_field(MessageUserSerializer())
    def get_user(self, obj: Message) -> dict | None:
        """Get user details for the message.

        Args:
            obj (Message): The message instance.

        Returns:
            dict | None: The user details including id, username, and email.
        """

        # If the message has a user
        if obj.user:
            # Return the user details with string UUID
            return {
                "id": str(obj.user.id),
                "username": obj.user.username,
                "email": obj.user.email,
            }

        # Return None if the message has no user
        return None

    # Get agent details
    @extend_schema_field(MessageAgentSerializer())
    def get_agent(self, obj: Message) -> dict | None:
        """Get agent details for the message.

        Args:
            obj (Message): The message instance.

        Returns:
            dict | None: The agent details including id and name.
        """

        # If the message has an agent
        if obj.agent:
            # Return the agent details with string UUID
            return {
                "id": str(obj.agent.id),
                "name": obj.agent.name,
            }

        # Return None if the message has no agent
        return None


# Message response schema for API documentation
class MessageResponseSchema(serializers.Serializer):
    """Message response schema for API documentation.

    This serializer defines the structure of message responses in the API documentation.

    Attributes:
        id (UUID): The message's ID.
        content (str): The message content.
        sender (str): The sender type (user or agent).
        session (UUID): The ID of the session this message belongs to.
        user (MessageUserSerializer): User details if sender is a user.
        agent (MessageAgentSerializer): Agent details if sender is an agent.
        created_at (datetime): The date and time the message was created.
        updated_at (datetime): The date and time the message was last updated.
    """

    # ID field
    id = serializers.UUIDField(
        help_text=_("Unique identifier for the message."),
    )

    # Content field
    content = serializers.CharField(
        help_text=_("Content of the message."),
    )

    # Sender field
    sender = serializers.ChoiceField(
        choices=Message.SenderType.choices,
        help_text=_("Sender type of the message (user or agent)."),
    )

    # Session field
    session = serializers.UUIDField(
        help_text=_("ID of the session this message belongs to."),
    )

    # Created at field
    created_at = serializers.DateTimeField(
        help_text=_("Timestamp when the message was created."),
    )

    # Updated at field
    updated_at = serializers.DateTimeField(
        help_text=_("Timestamp when the message was last updated."),
    )

    # User field using the proper serializer
    user = MessageUserSerializer(
        help_text=_("User details who sent the message."),
        required=False,
        allow_null=True,
    )

    # Agent field using the proper serializer
    agent = MessageAgentSerializer(
        help_text=_("Agent details who sent the message."),
        required=False,
        allow_null=True,
    )
