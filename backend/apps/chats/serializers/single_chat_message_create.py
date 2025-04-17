# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.chats.models import Message
from apps.chats.serializers.message import MessageResponseSchema
from apps.common.serializers import GenericResponseSerializer


# SingleChat message creation serializer
class SingleChatMessageCreateSerializer(serializers.ModelSerializer):
    """SingleChat message creation serializer.

    This serializer handles the creation of new messages in a single chat.
    It validates the sender type and sets the appropriate fields based on the sender.

    Attributes:
        content (CharField): The content of the message.
        sender (ChoiceField): The sender type of the message (user or agent).

    Meta:
        model (Message): The Message model.
        fields (list): The fields to include in the serializer.
        extra_kwargs (dict): Additional field configurations.

    Returns:
        Message: The newly created message instance.
    """

    # Meta class for SingleChatMessageCreateSerializer configuration
    class Meta:
        """Meta class for SingleChatMessageCreateSerializer configuration.

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
        2. The single chat exists.

        Args:
            attrs (dict): The attributes to validate.

        Returns:
            dict: The validated attributes.

        Raises:
            serializers.ValidationError: If validation fails.
        """

        # Get the single chat from the context
        single_chat = self.context.get("single_chat")

        # Check if single chat exists
        if not single_chat:
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        _("Single chat not found."),
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

        # Store the single chat in attrs for later use
        attrs["single_chat"] = single_chat

        # If the sender is a user
        if sender == Message.SenderType.USER:
            # Set the user to the single chat user
            attrs["user"] = single_chat.user

            # Set the agent to None
            attrs["agent"] = None

        # If the sender is an agent
        else:
            # Set the agent to the single chat agent
            attrs["agent"] = single_chat.agent

            # Set the user to None
            attrs["user"] = None

        # Set group chat to None
        attrs["group_chat"] = None

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


# SingleChat message creation success response serializer
class SingleChatMessageCreateSuccessResponseSerializer(GenericResponseSerializer):
    """SingleChat message creation success response serializer.

    This serializer defines the structure of the single chat message creation success response.
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


# SingleChat message creation error response serializer
class SingleChatMessageCreateErrorResponseSerializer(GenericResponseSerializer):
    """SingleChat message creation error response serializer.

    This serializer defines the structure of the single chat message creation error response.
    It includes a status code and error details.

    Attributes:
        status_code (int): The status code of the response.
        errors (SingleChatMessageCreateErrorsDetailSerializer): The validation errors.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Nested serializer defining the structure of the actual errors
    class SingleChatMessageCreateErrorsDetailSerializer(serializers.Serializer):
        """SingleChat Message Creation Errors detail serializer.

        Attributes:
            content (list): Errors related to the content field.
            sender (list): Errors related to the sender field.
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

        # Non-field errors
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Non-field specific errors."),
        )

    # Define the 'errors' field containing the validation error details
    errors = SingleChatMessageCreateErrorsDetailSerializer(
        help_text=_("Validation errors for the single chat message creation request."),
    )


# SingleChat message authentication error response serializer
class SingleChatMessageAuthErrorResponseSerializer(GenericResponseSerializer):
    """SingleChat message authentication error response serializer.

    This serializer defines the structure of the single chat message authentication error response.
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


# SingleChat message not found error response serializer
class SingleChatMessageNotFoundErrorResponseSerializer(GenericResponseSerializer):
    """SingleChat message not found error response serializer.

    This serializer defines the structure of the single chat message not found error response.
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
        default=_("Single chat not found."),
        read_only=True,
        help_text=_("Error message."),
    )


# SingleChat message permission denied response serializer
class SingleChatMessagePermissionDeniedResponseSerializer(GenericResponseSerializer):
    """SingleChat message permission denied response serializer.

    This serializer defines the structure of the single chat message permission denied response.
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
