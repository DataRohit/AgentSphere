# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.agents.models import Agent
from apps.chats.models import SingleChat
from apps.chats.serializers.single_chat import SingleChatResponseSchema
from apps.common.serializers import GenericResponseSerializer


# SingleChat update serializer
class SingleChatUpdateSerializer(serializers.ModelSerializer):
    """SingleChat update serializer.

    This serializer handles updating existing single chats. It validates
    that the chat exists and the user has permission to update it.

    Attributes:
        title (CharField): The title of the chat.
        agent_id (UUIDField): The ID of the agent to associate the chat with.
        is_public (BooleanField): Whether this chat is publicly visible to other users in the organization.

    Meta:
        model (SingleChat): The SingleChat model.
        fields (list): The fields to include in the serializer.

    Raises:
        serializers.ValidationError: If the user doesn't have permission to update this chat.
        serializers.ValidationError: If the agent doesn't exist or is not accessible.

    Returns:
        SingleChat: The updated single chat instance.
    """

    # Agent ID field for looking up and assigning the agent instance
    agent_id = serializers.UUIDField(
        required=False,
        help_text=_("ID of the agent to chat with."),
    )

    # Meta class for SingleChatUpdateSerializer configuration
    class Meta:
        """Meta class for SingleChatUpdateSerializer configuration.

        Attributes:
            model (SingleChat): The model class.
            fields (list): The fields to include in the serializer.
        """

        # Model to use for the serializer
        model = SingleChat

        # Fields to include in the serializer
        fields = [
            "title",
            "agent_id",
            "is_public",
        ]

        # Extra kwargs
        extra_kwargs = {
            "title": {"required": False},
            "is_public": {"required": False},
        }

    # Validate the serializer data
    def validate(self, attrs: dict) -> dict:
        """Validate the serializer data.

        This method validates that:
        1. The user has permission to update this chat.
        2. If a new agent is specified, it exists and the user has access to it.

        Args:
            attrs (dict): The attributes to validate.

        Returns:
            dict: The validated attributes.

        Raises:
            serializers.ValidationError: If validation fails.
        """

        # Get the user from the context
        user = self.context["request"].user

        # Get the single chat instance from the context
        single_chat = self.context["single_chat"]

        # Check if the user owns this chat or is part of the organization
        if single_chat.user != user and (
            not single_chat.organization
            or (user not in single_chat.organization.members.all() and user != single_chat.organization.owner)
        ):
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        _("You do not have permission to update this chat."),
                    ],
                },
            )

        # If a new agent ID is provided, validate it
        agent_id = attrs.get("agent_id")
        if agent_id:
            try:
                # Try to get the agent
                agent = Agent.objects.get(id=agent_id)

                # Check if the user is the organization owner or the creator of the agent
                if user not in (single_chat.organization.owner, agent.user):
                    # Raise a validation error
                    raise serializers.ValidationError(
                        {
                            "agent_id": [
                                _("Only the organization owner or the creator of the agent can use this agent."),
                            ],
                        },
                    )

                # Check if the agent belongs to the same organization
                if single_chat.organization and agent.organization and single_chat.organization != agent.organization:
                    # Raise a validation error
                    raise serializers.ValidationError(
                        {
                            "agent_id": [
                                _(
                                    "The agent must belong to the same organization as the chat.",
                                ),
                            ],
                        },
                    )

                # Store the agent in attrs for later use
                attrs["agent"] = agent

                # Remove the agent_id from attrs as it's not a field in the SingleChat model
                del attrs["agent_id"]

            except Agent.DoesNotExist:
                # Raise a validation error
                raise serializers.ValidationError(
                    {
                        "agent_id": [
                            _("Agent not found."),
                        ],
                    },
                ) from None

        # Return the validated data
        return attrs

    # Update the single chat with the validated data
    def update(self, instance: SingleChat, validated_data: dict) -> SingleChat:
        """Update the single chat with the validated data.

        Args:
            instance (SingleChat): The existing single chat instance.
            validated_data (dict): The validated data.

        Returns:
            SingleChat: The updated single chat instance.
        """

        # Update the single chat with the validated data
        for key, value in validated_data.items():
            setattr(instance, key, value)

        # Save the single chat
        instance.save()

        # Return the updated single chat
        return instance


# SingleChat update success response serializer
class SingleChatUpdateSuccessResponseSerializer(GenericResponseSerializer):
    """SingleChat update success response serializer.

    This serializer defines the structure of the single chat update success response.
    It includes a status code and a single chat object.

    Attributes:
        status_code (int): The status code of the response.
        single_chat (SingleChatResponseSchema): The updated single chat with detailed information.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Chat data
    chat = SingleChatResponseSchema(
        help_text=_(
            "The updated chat with detailed organization, user, and agent information.",
        ),
    )


# SingleChat update error response serializer
class SingleChatUpdateErrorResponseSerializer(GenericResponseSerializer):
    """SingleChat update error response serializer.

    This serializer defines the structure of the single chat update error response.
    It includes a status code and error details.

    Attributes:
        status_code (int): The status code of the response.
        errors (SingleChatUpdateErrorsDetailSerializer): The detailed error serializer.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Nested serializer defining the structure of the actual errors
    class SingleChatUpdateErrorsDetailSerializer(serializers.Serializer):
        """SingleChat Update Errors detail serializer.

        Attributes:
            title (list): Errors related to the title field.
            agent_id (list): Errors related to the agent ID field.
            is_public (list): Errors related to the is_public field.
            non_field_errors (list): Non-field specific errors.
        """

        # Title field
        title = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the title field."),
        )

        # Agent ID field
        agent_id = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the agent ID field."),
        )

        # Is public field
        is_public = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the is_public field."),
        )

        # Non-field errors
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Non-field specific errors."),
        )

    # Define the 'errors' field containing the validation error details
    errors = SingleChatUpdateErrorsDetailSerializer(
        help_text=_("Validation errors for the single chat update request."),
    )


# SingleChat not found error response serializer
class SingleChatNotFoundErrorResponseSerializer(GenericResponseSerializer):
    """SingleChat not found error response serializer.

    This serializer defines the structure of the single chat not found error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response (404 Not Found).
        error (str): An error message explaining that the single chat was not found.
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
        help_text=_("Error message explaining that the single chat was not found."),
    )


# SingleChat auth error response serializer
class SingleChatAuthErrorResponseSerializer(GenericResponseSerializer):
    """SingleChat auth error response serializer.

    This serializer defines the structure of the authentication error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response (401 Unauthorized).
        error (str): An error message explaining the authentication error.
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
        help_text=_("Error message explaining the authentication error."),
    )


# Permission denied error response serializer
class SingleChatPermissionDeniedResponseSerializer(GenericResponseSerializer):
    """Permission denied error response serializer.

    This serializer defines the structure of the permission denied error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response (403 Forbidden).
        error (str): An error message explaining the permission denial.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_403_FORBIDDEN,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("You do not have permission to update this chat."),
        read_only=True,
        help_text=_("Error message explaining the permission denial."),
    )
