# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.agents.models import Agent
from apps.chats.models import GroupChat
from apps.chats.serializers.group_chat import GroupChatResponseSchema
from apps.common.serializers import GenericResponseSerializer
from apps.organization.models import Organization


# GroupChat creation serializer
class GroupChatCreateSerializer(serializers.ModelSerializer):
    """GroupChat creation serializer.

    This serializer handles the creation of new group chats between a user and multiple agents.
    It validates that the user is a member of the specified organization and has access
    to the specified agents.

    Attributes:
        organization_id (UUIDField): The ID of the organization to associate the chat with.
        title (CharField): The title of the chat.
        agent_ids (ListField): The IDs of the agents to associate the chat with.
        is_public (BooleanField): Whether this chat is publicly visible to other users in the organization.

    Meta:
        model (GroupChat): The GroupChat model.
        fields (list): The fields to include in the serializer.
        extra_kwargs (dict): Additional field configurations.

    Raises:
        serializers.ValidationError: If user is not a member of the organization.
        serializers.ValidationError: If agents don't exist or user doesn't have access.

    Returns:
        GroupChat: The newly created group chat instance.
    """

    # Organization ID field
    organization_id = serializers.UUIDField(
        required=True,
        help_text=_("ID of the organization to associate the chat with."),
    )

    # Agent IDs field
    agent_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        help_text=_("IDs of the agents to chat with."),
    )

    # Meta class for GroupChatCreateSerializer configuration
    class Meta:
        """Meta class for GroupChatCreateSerializer configuration.

        Attributes:
            model (GroupChat): The model class.
            fields (list): The fields to include in the serializer.
            extra_kwargs (dict): Additional field configurations.
        """

        # Model to use for the serializer
        model = GroupChat

        # Fields to include in the serializer
        fields = [
            "organization_id",
            "title",
            "agent_ids",
            "is_public",
        ]

        # Extra kwargs
        extra_kwargs = {
            "title": {"required": True},
            "is_public": {"required": False, "default": False},
        }

    # Validate the serializer data
    def validate(self, attrs: dict) -> dict:
        """Validate the serializer data.

        This method validates that:
        1. The user is a member of the specified organization.
        2. The specified agents exist and user has access to them.
        3. The agents belong to the same organization.

        Args:
            attrs (dict): The attributes to validate.

        Returns:
            dict: The validated attributes.

        Raises:
            serializers.ValidationError: If validation fails.
        """

        # Get the user from the context
        user = self.context["request"].user

        # Get the organization ID
        organization_id = attrs.get("organization_id")

        # Get the agent IDs
        agent_ids = attrs.get("agent_ids")

        # Validate that at least one agent ID is provided
        if not agent_ids:
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "agent_ids": [
                        _("At least one agent ID must be provided."),
                    ],
                },
            )

        try:
            # Try to get the organization
            organization = Organization.objects.get(id=organization_id)

            # Check if the user is a member of the organization
            if user != organization.owner and user not in organization.members.all():
                # Raise a validation error
                raise serializers.ValidationError(
                    {
                        "organization_id": [
                            _("You are not a member of this organization."),
                        ],
                    },
                )

            # Validate that the agents exist and belong to the organization
            agents = []
            for agent_id in agent_ids:
                try:
                    # Try to get the agent
                    agent = Agent.objects.get(id=agent_id)

                    # Check if the agent belongs to the organization
                    if agent.organization != organization:
                        # Raise a validation error
                        raise serializers.ValidationError(
                            {
                                "agent_ids": [
                                    _(
                                        "Agent with ID {agent_id} does not belong to the specified organization.",
                                    ).format(agent_id=agent_id),
                                ],
                            },
                        )

                    # Check if the user is the organization owner or the creator of the agent
                    if user not in (organization.owner, agent.user):
                        # Raise a validation error
                        raise serializers.ValidationError(
                            {
                                "agent_ids": [
                                    _(
                                        "Only the organization owner or the creator of the agent can use agent with ID {agent_id}.",  # noqa: E501
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

            # Store the organization in attrs for later use
            attrs["organization"] = organization

            # Store the user in attrs for later use
            attrs["user"] = user

            # Store the agents in attrs for later use
            attrs["agents"] = agents

            # Remove the organization_id and agent_ids from attrs
            del attrs["organization_id"]
            del attrs["agent_ids"]

        except Organization.DoesNotExist:
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "organization_id": [
                        _("Organization not found."),
                    ],
                },
            ) from None

        # Return the validated data
        return attrs

    # Create a new group chat
    def create(self, validated_data: dict) -> GroupChat:
        """Create a new group chat.

        This method creates a new group chat with the validated data.

        Args:
            validated_data (dict): The validated data.

        Returns:
            GroupChat: The newly created group chat.
        """

        # Get the agents from the validated data
        agents = validated_data.pop("agents")

        # Create a new group chat
        group_chat = GroupChat.objects.create(**validated_data)

        # Add the agents to the group chat
        group_chat.agents.set(agents)

        # Return the group chat
        return group_chat


# GroupChat creation success response serializer
class GroupChatCreateSuccessResponseSerializer(GenericResponseSerializer):
    """GroupChat creation success response serializer.

    This serializer defines the structure of the group chat creation success response.
    It includes a status code and a group chat object.

    Attributes:
        status_code (int): The status code of the response.
        group_chat (GroupChatResponseSchema): The newly created group chat with necessary information.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_201_CREATED,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Chat data
    chat = GroupChatResponseSchema(
        help_text=_(
            "The newly created chat with detailed organization, user, and agent information.",
        ),
    )


# GroupChat auth error response serializer
class GroupChatAuthErrorResponseSerializer(GenericResponseSerializer):
    """GroupChat auth error response serializer.

    This serializer defines the structure of the authentication error response.
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
        help_text=_("Error message for the response."),
    )


# GroupChat creation error response serializer
class GroupChatCreateErrorResponseSerializer(GenericResponseSerializer):
    """GroupChat creation error response serializer (for schema).

    This serializer defines the structure of the wrapped validation error response
    as it would be formatted for documentation purposes.

    Attributes:
        status_code (int): The status code of the response.
        errors (GroupChatCreateErrorsDetailSerializer): The errors detail serializer.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Nested serializer defining the structure of the actual errors
    class GroupChatCreateErrorsDetailSerializer(serializers.Serializer):
        """GroupChat Creation Errors detail serializer.

        Attributes:
            organization_id (list): Errors related to the organization ID field.
            title (list): Errors related to the title field.
            agent_ids (list): Errors related to the agent IDs field.
            non_field_errors (list): Non-field specific errors.
        """

        # Organization ID field
        organization_id = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the organization ID field."),
        )

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
    errors = GroupChatCreateErrorsDetailSerializer(
        help_text=_("Validation errors for the group chat creation request."),
    )
