# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.chats.models import Message
from apps.chats.serializers.message import MessageResponseSchema
from apps.common.serializers import GenericResponseSerializer


# SingleChat message update serializer
class SingleChatMessageUpdateSerializer(serializers.ModelSerializer):
    """SingleChat message update serializer.

    This serializer handles updating existing messages in a single chat.
    It validates that the message exists and the user has permission to update it.
    Only the content field can be updated.

    Attributes:
        content (CharField): The content of the message.

    Meta:
        model (Message): The Message model.
        fields (list): The fields to include in the serializer.

    Raises:
        serializers.ValidationError: If the user doesn't have permission to update this message.

    Returns:
        Message: The updated message instance.
    """

    # Meta class for SingleChatMessageUpdateSerializer configuration
    class Meta:
        """Meta class for SingleChatMessageUpdateSerializer configuration.

        Attributes:
            model (Message): The model class.
            fields (list): The fields to include in the serializer.
        """

        # Model to use for the serializer
        model = Message

        # Fields to include in the serializer - only content can be updated
        fields = [
            "content",
        ]

        # Extra kwargs
        extra_kwargs = {
            "content": {"required": True},
        }

    # Validate the serializer data
    def validate(self, attrs: dict) -> dict:
        """Validate the serializer data.

        This method validates that:
        1. The user has permission to update this message.
        2. If the message is a user message, only the user who created the chat can update it.
        3. If the message is an agent message, only the organization owner can update it.

        Args:
            attrs (dict): The attributes to validate.

        Returns:
            dict: The validated attributes.

        Raises:
            serializers.ValidationError: If validation fails.
        """

        # Get the user from the context
        user = self.context["request"].user

        # Get the message instance from the context
        message = self.context["message"]

        # Get the single chat from the message
        single_chat = message.single_chat

        # Check if the user is the owner of the organization
        is_org_owner = single_chat.organization and user == single_chat.organization.owner

        # Check if the user is the creator of the chat
        is_chat_creator = user == single_chat.user

        # If the user is neither the chat creator nor the organization owner, deny permission
        if not (is_chat_creator or is_org_owner):
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        _("You do not have permission to update this message."),
                    ],
                },
            )

        # If the message is from an agent and the user is not the organization owner, deny permission
        if message.sender == Message.SenderType.AGENT and not is_org_owner:
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        _("Only the organization owner can update agent messages."),
                    ],
                },
            )

        # If the message is from a user and the user is not the chat creator, deny permission
        if message.sender == Message.SenderType.USER and not is_chat_creator and not is_org_owner:
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        _("Only the chat creator can update user messages."),
                    ],
                },
            )

        # Return the validated data
        return attrs

    # Update the message with the validated data
    def update(self, instance: Message, validated_data: dict) -> Message:
        """Update the message with the validated data.

        Args:
            instance (Message): The existing message instance.
            validated_data (dict): The validated data.

        Returns:
            Message: The updated message instance.
        """

        # Update the content field
        instance.content = validated_data.get("content", instance.content)

        # Save the message
        instance.save()

        # Return the updated message
        return instance


# SingleChat message update success response serializer
class SingleChatMessageUpdateSuccessResponseSerializer(GenericResponseSerializer):
    """SingleChat message update success response serializer.

    This serializer defines the structure of the single chat message update success response.
    It includes a status code and a message object.

    Attributes:
        status_code (int): The status code of the response.
        message (MessageResponseSchema): The updated message with necessary information.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Message field
    message = MessageResponseSchema(
        help_text=_("The updated message."),
    )


# SingleChat message update error response serializer
class SingleChatMessageUpdateErrorResponseSerializer(GenericResponseSerializer):
    """SingleChat message update error response serializer.

    This serializer defines the structure of the single chat message update error response.
    It includes a status code and error details.

    Attributes:
        status_code (int): The status code of the response.
        errors (SingleChatMessageUpdateErrorsDetailSerializer): The validation errors.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Nested serializer defining the structure of the actual errors
    class SingleChatMessageUpdateErrorsDetailSerializer(serializers.Serializer):
        """SingleChat Message Update Errors detail serializer.

        Attributes:
            content (list): Errors related to the content field.
            non_field_errors (list): Non-field specific errors.
        """

        # Content field
        content = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the content field."),
        )

        # Non-field errors
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Non-field specific errors."),
        )

    # Define the 'errors' field containing the validation error details
    errors = SingleChatMessageUpdateErrorsDetailSerializer(
        help_text=_("Validation errors for the single chat message update request."),
    )


# SingleChat message authentication error response serializer
class SingleChatMessageUpdateAuthErrorResponseSerializer(GenericResponseSerializer):
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
class SingleChatMessageUpdateNotFoundErrorResponseSerializer(GenericResponseSerializer):
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
        default=_("Message not found."),
        read_only=True,
        help_text=_("Error message."),
    )


# SingleChat message permission denied response serializer
class SingleChatMessageUpdatePermissionDeniedResponseSerializer(GenericResponseSerializer):
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
        default=_("You do not have permission to update this message."),
        read_only=True,
        help_text=_("Error message."),
    )
