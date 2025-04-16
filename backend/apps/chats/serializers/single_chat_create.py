# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.agents.models import Agent
from apps.chats.models import SingleChat
from apps.chats.serializers.single_chat import SingleChatResponseSchema
from apps.common.serializers import GenericResponseSerializer
from apps.organization.models import Organization


# SingleChat creation serializer
class SingleChatCreateSerializer(serializers.ModelSerializer):
    """SingleChat creation serializer.

    This serializer handles the creation of new single chats between a user and an agent.
    It validates that the user is a member of the specified organization and has access
    to the specified agent.

    Attributes:
        organization_id (UUIDField): The ID of the organization to associate the chat with.
        title (CharField): The title of the chat.
        agent_id (UUIDField): The ID of the agent to associate the chat with.
        is_public (BooleanField): Whether this chat is publicly visible to other users in the organization.

    Meta:
        model (SingleChat): The SingleChat model.
        fields (list): The fields to include in the serializer.
        extra_kwargs (dict): Additional field configurations.

    Raises:
        serializers.ValidationError: If user is not a member of the organization.
        serializers.ValidationError: If agent doesn't exist or user doesn't have access.

    Returns:
        SingleChat: The newly created single chat instance.
    """

    # Organization ID field
    organization_id = serializers.UUIDField(
        required=True,
        help_text=_("ID of the organization to associate the chat with."),
    )

    # Agent ID field
    agent_id = serializers.UUIDField(
        required=True,
        help_text=_("ID of the agent to chat with."),
    )

    # Meta class for SingleChatCreateSerializer configuration
    class Meta:
        """Meta class for SingleChatCreateSerializer configuration.

        Attributes:
            model (SingleChat): The model class.
            fields (list): The fields to include in the serializer.
            extra_kwargs (dict): Additional field configurations.
        """

        # Model to use for the serializer
        model = SingleChat

        # Fields to include in the serializer
        fields = [
            "organization_id",
            "title",
            "agent_id",
            "is_public",
        ]

        # Extra kwargs
        extra_kwargs = {
            "title": {"required": True},
            "is_public": {"required": False, "default": False},
        }

    # Validate the serializer data
    def validate(self, attrs):
        """Validate the serializer data.

        This method validates that:
        1. The user is a member of the specified organization.
        2. The specified agent exists and user has access to it.
        3. The agent belongs to the same organization.

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

        # Get the agent ID
        agent_id = attrs.get("agent_id")

        try:
            # Try to get the organization
            organization = Organization.objects.get(id=organization_id)

            # Check if the user is a member of the organization
            if user not in organization.members.all() and user != organization.owner:
                # Raise a validation error
                raise serializers.ValidationError(
                    {
                        "organization_id": [
                            _("You are not a member of this organization."),
                        ],
                    },
                ) from None

            try:
                # Try to get the agent
                agent = Agent.objects.get(id=agent_id)

                # Check if the agent is public or belongs to the user
                if not agent.is_public and agent.user != user:
                    # Raise a validation error
                    raise serializers.ValidationError(
                        {
                            "agent_id": [
                                _("You do not have access to this agent."),
                            ],
                        },
                    ) from None

                # Check if the agent belongs to the same organization
                if agent.organization != organization:
                    # Raise a validation error
                    raise serializers.ValidationError(
                        {
                            "agent_id": [
                                _(
                                    "The agent must belong to the same organization as the chat.",
                                ),
                            ],
                        },
                    ) from None

                # Store the agent in attrs for later use
                attrs["agent"] = agent

            except Agent.DoesNotExist:
                # Raise a validation error
                raise serializers.ValidationError(
                    {
                        "agent_id": [
                            _("Agent not found."),
                        ],
                    },
                ) from None

            # Store the organization in attrs for later use
            attrs["organization"] = organization

            # Store the user in attrs for later use
            attrs["user"] = user

            # Remove the organization_id and agent_id from attrs
            del attrs["organization_id"]
            del attrs["agent_id"]

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

    # Create method to create a new single chat
    def create(self, validated_data):
        """Create a new single chat with the validated data.

        Args:
            validated_data (dict): The validated data.

        Returns:
            SingleChat: The newly created single chat.
        """

        # Create and return a new single chat with the validated data
        return SingleChat.objects.create(**validated_data)


# SingleChat creation success response serializer
class SingleChatCreateSuccessResponseSerializer(GenericResponseSerializer):
    """SingleChat creation success response serializer.

    This serializer defines the structure of the single chat creation success response.
    It includes a status code and a single chat object.

    Attributes:
        status_code (int): The status code of the response.
        single_chat (SingleChatResponseSchema): The newly created single chat with necessary information.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_201_CREATED,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # SingleChat data
    single_chat = SingleChatResponseSchema(
        help_text=_(
            "The newly created single chat with necessary organization, user, and agent information.",
        ),
    )


# SingleChat creation error response serializer
class SingleChatCreateErrorResponseSerializer(GenericResponseSerializer):
    """SingleChat creation error response serializer (for schema).

    This serializer defines the structure of the wrapped validation error response
    as it would be formatted for documentation purposes.

    Attributes:
        status_code (int): The status code of the response.
        errors (SingleChatCreateErrorsDetailSerializer): The errors detail serializer.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Nested serializer defining the structure of the actual errors
    class SingleChatCreateErrorsDetailSerializer(serializers.Serializer):
        """SingleChat Creation Errors detail serializer.

        Attributes:
            organization_id (list): Errors related to the organization ID field.
            title (list): Errors related to the title field.
            agent_id (list): Errors related to the agent ID field.
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

        # Agent ID field
        agent_id = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the agent ID field."),
        )

        # Non-field errors
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Non-field specific errors."),
        )

    # Define the 'errors' field containing the validation error details
    errors = SingleChatCreateErrorsDetailSerializer(
        help_text=_("Validation errors for the single chat creation request."),
    )


# Authentication error response serializer
class SingleChatAuthErrorResponseSerializer(GenericResponseSerializer):
    """Authentication error response serializer.

    This serializer defines the structure of the authentication error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response (401 Unauthorized).
        error (str): An error message explaining the authentication failure.
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
        help_text=_("Error message explaining the authentication failure."),
    )
