# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.agents.models import Agent
from apps.chats.models import Message
from apps.chats.serializers.message import MessageResponseSchema
from apps.common.serializers import GenericResponseSerializer


# GroupChat message creation serializer
class GroupChatMessageCreateSerializer(serializers.ModelSerializer):
    """GroupChat message creation serializer.

    This serializer handles the creation of new messages in a group chat.
    It validates the sender type and sets the appropriate fields based on the sender.
    If the sender is an agent, it validates that the agent is part of the group chat.
    The session field is required and cannot be updated after creation.

    Attributes:
        content (CharField): The content of the message.
        sender (ChoiceField): The sender type of the message (user or agent).
        agent_id (UUIDField): The ID of the agent sending the message (required if sender is agent).
        session_id (UUIDField): The ID of the session this message belongs to.

    Meta:
        model (Message): The Message model.
        fields (list): The fields to include in the serializer.
        extra_kwargs (dict): Additional field configurations.

    Returns:
        Message: The newly created message instance.
    """

    # Agent ID field (required if sender is agent)
    agent_id = serializers.UUIDField(
        help_text=_("ID of the agent sending the message (required if sender is agent)."),
        required=False,
        write_only=True,
    )

    # Session ID field (not a model field, used for validation)
    session_id = serializers.UUIDField(
        required=True,
        help_text=_("ID of the session this message belongs to."),
        write_only=True,
    )

    # Meta class for GroupChatMessageCreateSerializer configuration
    class Meta:
        """Meta class for GroupChatMessageCreateSerializer configuration.

        Attributes:
            model (Message): The model class.
            fields (list): The fields to include in the serializer.
            extra_kwargs (dict): Additional field configurations.
        """

        # Model to use for the serializer
        model = Message

        # Fields to include in the serializer
        fields = [
            "content",
            "sender",
            "agent_id",
            "session_id",
        ]

        # Extra kwargs
        extra_kwargs = {
            "content": {"required": True},
            "sender": {"required": True},
        }

    # Validate the serializer data
    def validate(self, attrs: dict) -> dict:
        """Validate the serializer data.

        This method validates that:
        1. The sender type is valid.
        2. The group chat exists.
        3. If sender is agent, the agent_id is provided and the agent is part of the group chat.
        4. The session exists and is associated with the group chat.

        Args:
            attrs (dict): The attributes to validate.

        Returns:
            dict: The validated attributes.

        Raises:
            serializers.ValidationError: If validation fails.
        """
        from apps.conversation.models import Session

        # Get the group chat from the context
        group_chat = self.context.get("group_chat")

        # Check if group chat exists
        if not group_chat:
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        _("Group chat not found."),
                    ],
                },
            )

        # Get the sender type
        sender = attrs.get("sender")

        # Validate sender type
        if sender not in [Message.SenderType.USER, Message.SenderType.AGENT]:
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "sender": [
                        _("Invalid sender type."),
                    ],
                },
            )

        # Get the session ID
        session_id = attrs.pop("session_id", None)

        # Check if session ID is provided
        if not session_id:
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "session_id": [
                        _("Session ID is required."),
                    ],
                },
            )

        try:
            # Get the session
            session = Session.objects.get(id=session_id)

            # Check if the session is associated with the group chat
            if session.group_chat != group_chat:
                # Raise a validation error
                raise serializers.ValidationError(
                    {
                        "session_id": [
                            _("Session must be associated with the specified group chat."),
                        ],
                    },
                )

            # Store the session in attrs for later use
            attrs["session"] = session

        except Session.DoesNotExist:
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "session_id": [
                        _("Session not found."),
                    ],
                },
            ) from None

        # Store the group chat in attrs for later use
        attrs["group_chat"] = group_chat

        # Set single_chat to None
        attrs["single_chat"] = None

        # If the sender is a user
        if sender == Message.SenderType.USER:
            # Set the user to the group chat user
            attrs["user"] = group_chat.user

            # Set the agent to None
            attrs["agent"] = None

        # If the sender is an agent
        else:
            # Check if agent_id is provided
            agent_id = attrs.get("agent_id")
            if not agent_id:
                # Raise a validation error
                raise serializers.ValidationError(
                    {
                        "agent_id": [
                            _("Agent ID is required when sender is agent."),
                        ],
                    },
                )

            try:
                # Try to get the agent
                agent = Agent.objects.get(id=agent_id)

                # Check if the agent is part of the group chat
                if agent not in group_chat.agents.all():
                    # Raise a validation error
                    raise serializers.ValidationError(
                        {
                            "agent_id": [
                                _("Agent is not part of this group chat."),
                            ],
                        },
                    )

                # Set the agent
                attrs["agent"] = agent

                # Set the user to None
                attrs["user"] = None

            except Agent.DoesNotExist as err:
                # Raise a validation error
                raise serializers.ValidationError(
                    {
                        "agent_id": [
                            _("Agent not found."),
                        ],
                    },
                ) from err

            # Remove agent_id from attrs as it's not a field in the Message model
            attrs.pop("agent_id", None)

        # Return the validated data
        return attrs

    # Create method to create a new message
    def create(self, validated_data: dict) -> Message:
        """Create a new message with the validated data.

        Args:
            validated_data (dict): The validated data.

        Returns:
            Message: The newly created message.
        """

        # Create and return a new message with the validated data
        return Message.objects.create(**validated_data)


# GroupChat message creation success response serializer
class GroupChatMessageCreateSuccessResponseSerializer(GenericResponseSerializer):
    """GroupChat message creation success response serializer.

    This serializer defines the structure of the group chat message creation success response.
    It includes a status code and a message object.

    Attributes:
        status_code (int): The status code of the response.
        message (MessageResponseSchema): The newly created message with necessary information.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_201_CREATED,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Message field
    message = MessageResponseSchema(
        help_text=_("The newly created message."),
    )


# GroupChat message creation error response serializer
class GroupChatMessageCreateErrorResponseSerializer(GenericResponseSerializer):
    """GroupChat message creation error response serializer.

    This serializer defines the structure of the group chat message creation error response.
    It includes a status code and error details.

    Attributes:
        status_code (int): The status code of the response.
        errors (GroupChatMessageCreateErrorsDetailSerializer): The validation errors.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Nested serializer defining the structure of the actual errors
    class GroupChatMessageCreateErrorsDetailSerializer(serializers.Serializer):
        """GroupChat Message Creation Errors detail serializer.

        Attributes:
            content (list): Errors related to the content field.
            sender (list): Errors related to the sender field.
            agent_id (list): Errors related to the agent_id field.
            session_id (list): Errors related to the session_id field.
            non_field_errors (list): Non-field specific errors.
        """

        # Content field
        content = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the content field."),
        )

        # Sender field
        sender = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the sender field."),
        )

        # Agent ID field
        agent_id = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the agent_id field."),
        )

        # Session ID field
        session_id = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the session_id field."),
        )

        # Non-field errors
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Non-field specific errors."),
        )

    # Define the 'errors' field containing the validation error details
    errors = GroupChatMessageCreateErrorsDetailSerializer(
        help_text=_("Validation errors for the group chat message creation request."),
    )


# GroupChat message authentication error response serializer
class GroupChatMessageAuthErrorResponseSerializer(GenericResponseSerializer):
    """GroupChat message authentication error response serializer.

    This serializer defines the structure of the group chat message authentication error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response.
        error (str): The error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_401_UNAUTHORIZED,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("Authentication credentials were not provided."),
        read_only=True,
        help_text=_("Error message."),
    )


# GroupChat message not found error response serializer
class GroupChatMessageNotFoundErrorResponseSerializer(GenericResponseSerializer):
    """GroupChat message not found error response serializer.

    This serializer defines the structure of the group chat message not found error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response.
        error (str): The error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_404_NOT_FOUND,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("Group chat not found."),
        read_only=True,
        help_text=_("Error message."),
    )


# GroupChat message permission denied response serializer
class GroupChatMessagePermissionDeniedResponseSerializer(GenericResponseSerializer):
    """GroupChat message permission denied response serializer.

    This serializer defines the structure of the group chat message permission denied response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response.
        error (str): The error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_403_FORBIDDEN,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("You do not have permission to create messages in this chat."),
        read_only=True,
        help_text=_("Error message."),
    )
