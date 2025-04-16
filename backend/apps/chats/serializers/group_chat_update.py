# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.agents.models import Agent
from apps.chats.models import GroupChat
from apps.chats.serializers.group_chat import GroupChatResponseSchema
from apps.common.serializers import GenericResponseSerializer


# GroupChat update serializer
class GroupChatUpdateSerializer(serializers.ModelSerializer):
    """GroupChat update serializer.

    This serializer handles updating existing group chats. It validates
    that the chat exists and the user has permission to update it.

    Attributes:
        title (CharField): The title of the chat.
        agent_ids (ListField): The IDs of the agents to associate the chat with.
        is_public (BooleanField): Whether this chat is publicly visible to other users in the organization.

    Meta:
        model (GroupChat): The GroupChat model.
        fields (list): The fields to include in the serializer.

    Raises:
        serializers.ValidationError: If the user doesn't have permission to update this chat.
        serializers.ValidationError: If the agents don't exist or are not accessible.

    Returns:
        GroupChat: The updated group chat instance.
    """

    # Agent IDs field for looking up and assigning the agent instances
    agent_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text=_("IDs of the agents to chat with."),
    )

    # Meta class for GroupChatUpdateSerializer configuration
    class Meta:
        """Meta class for GroupChatUpdateSerializer configuration.

        Attributes:
            model (GroupChat): The model class.
            fields (list): The fields to include in the serializer.
        """

        # Model to use for the serializer
        model = GroupChat

        # Fields to include in the serializer
        fields = [
            "title",
            "agent_ids",
            "is_public",
        ]

        # Extra kwargs
        extra_kwargs = {
            "title": {"required": False},
            "is_public": {"required": False},
        }

    # Validate the serializer data
    def validate(self, attrs):
        """Validate the serializer data.

        This method validates that:
        1. The user has permission to update this chat.
        2. If new agents are specified, they exist and the user has access to them.

        Args:
            attrs (dict): The attributes to validate.

        Returns:
            dict: The validated attributes.

        Raises:
            serializers.ValidationError: If validation fails.
        """

        # Get the user from the context
        user = self.context["request"].user

        # Get the group chat instance from the context
        group_chat = self.context["group_chat"]

        # Check if the user owns this chat or is part of the organization
        if group_chat.user != user and (
            not group_chat.organization
            or (user not in group_chat.organization.members.all() and user != group_chat.organization.owner)
        ):
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        _("You do not have permission to update this chat."),
                    ],
                },
            )

        # If new agent IDs are provided, validate them
        agent_ids = attrs.get("agent_ids")
        if agent_ids:
            # Validate that at least one agent ID is provided
            if not agent_ids:
                raise serializers.ValidationError(
                    {
                        "agent_ids": [
                            _("At least one agent ID must be provided."),
                        ],
                    },
                )

            # Validate each agent ID
            agents = []
            for agent_id in agent_ids:
                try:
                    # Try to get the agent
                    agent = Agent.objects.get(id=agent_id)

                    # Check if the agent is public or belongs to the user
                    if not agent.is_public and agent.user != user:
                        # Raise a validation error
                        raise serializers.ValidationError(
                            {
                                "agent_ids": [
                                    _(
                                        "You do not have access to agent with ID {agent_id}.",
                                    ).format(agent_id=agent_id),
                                ],
                            },
                        )

                    # Check if the agent belongs to the same organization
                    if group_chat.organization and agent.organization and group_chat.organization != agent.organization:
                        # Raise a validation error
                        raise serializers.ValidationError(
                            {
                                "agent_ids": [
                                    _(
                                        "Agent with ID {agent_id} must belong to the same organization as the chat.",
                                    ).format(agent_id=agent_id),
                                ],
                            },
                        )

                    # Add the agent to the list
                    agents.append(agent)

                except Agent.DoesNotExist:
                    # Raise a validation error
                    raise serializers.ValidationError(
                        {
                            "agent_ids": [
                                _(
                                    "Agent with ID {agent_id} not found.",
                                ).format(agent_id=agent_id),
                            ],
                        },
                    ) from None

            # Store the agents in attrs for later use
            attrs["agents"] = agents
            # Remove the agent_ids from attrs
            del attrs["agent_ids"]

        # Return the validated data
        return attrs

    # Update the group chat with the validated data
    def update(self, instance, validated_data):
        """Update the group chat with the validated data.

        Args:
            instance (GroupChat): The existing group chat instance.
            validated_data (dict): The validated data.

        Returns:
            GroupChat: The updated group chat instance.
        """

        # Get the agents from the validated data
        agents = validated_data.pop("agents", None)

        # Update the group chat with the validated data
        for key, value in validated_data.items():
            setattr(instance, key, value)

        # Save the group chat
        instance.save()

        # If agents are provided, update the agents
        if agents is not None:
            # Update the agents
            instance.agents.set(agents)

        # Return the updated group chat
        return instance


# GroupChat update success response serializer
class GroupChatUpdateSuccessResponseSerializer(GenericResponseSerializer):
    """GroupChat update success response serializer.

    This serializer defines the structure of the group chat update success response.
    It includes a status code and a group chat object.

    Attributes:
        status_code (int): The status code of the response.
        group_chat (GroupChatResponseSchema): The updated group chat with detailed information.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Chat data
    chat = GroupChatResponseSchema(
        help_text=_(
            "The updated chat with detailed organization, user, and agent information.",
        ),
    )


# GroupChat update error response serializer
class GroupChatUpdateErrorResponseSerializer(GenericResponseSerializer):
    """GroupChat update error response serializer.

    This serializer defines the structure of the group chat update error response.
    It includes a status code and error details.

    Attributes:
        status_code (int): The status code of the response.
        errors (GroupChatUpdateErrorsDetailSerializer): The detailed error serializer.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Nested serializer defining the structure of the actual errors
    class GroupChatUpdateErrorsDetailSerializer(serializers.Serializer):
        """GroupChat Update Errors detail serializer.

        Attributes:
            title (list): Errors related to the title field.
            agent_ids (list): Errors related to the agent IDs field.
            is_public (list): Errors related to the is_public field.
            non_field_errors (list): Non-field specific errors.
        """

        # Title field
        title = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the title field."),
        )

        # Agent IDs field
        agent_ids = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the agent IDs field."),
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
    errors = GroupChatUpdateErrorsDetailSerializer(
        help_text=_("Validation errors for the group chat update request."),
    )


# GroupChat not found error response serializer
class GroupChatNotFoundErrorResponseSerializer(GenericResponseSerializer):
    """GroupChat not found error response serializer.

    This serializer defines the structure of the group chat not found error response.
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
        help_text=_("Error message for the response."),
    )


# GroupChat permission denied response serializer
class GroupChatPermissionDeniedResponseSerializer(GenericResponseSerializer):
    """GroupChat permission denied response serializer.

    This serializer defines the structure of the permission denied error response.
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
        default=_("You do not have permission to update this chat."),
        read_only=True,
        help_text=_("Error message for the response."),
    )
