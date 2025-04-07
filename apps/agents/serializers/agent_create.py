# Third-party imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers, status

# Project imports
from apps.agents.models import LLM, Agent
from apps.agents.serializers.agent import AgentResponseSchema
from apps.common.serializers import GenericResponseSerializer
from apps.organization.models import Organization


# Agent creation serializer
class AgentCreateSerializer(serializers.ModelSerializer):
    """Agent creation serializer.

    This serializer handles the creation of new AI agents. It validates that
    the user is a member of the specified organization and has not exceeded
    the maximum number of agents they can create (10 total, with max 5 public).

    Attributes:
        organization_id (UUIDField): The ID of the organization to associate the agent with.
        name (CharField): The name of the agent.
        description (TextField): A description of the agent.
        system_prompt (TextField): The system prompt used for the agent.
        is_public (BooleanField): Whether the agent is publicly visible.
        llm_id (UUIDField): The ID of the LLM to associate the agent with.

    Meta:
        model (Agent): The Agent model.
        fields (list): The fields to include in the serializer.
        extra_kwargs (dict): Additional field configurations.

    Raises:
        serializers.ValidationError: If user is not a member of the organization.
        serializers.ValidationError: If user has already created maximum agents.
        serializers.ValidationError: If LLM doesn't exist or user doesn't have access.

    Returns:
        Agent: The newly created agent instance.
    """

    # Maximum number of agents per organization
    MAX_AGENTS_PER_ORGANIZATION = 10

    # Maximum number of public agents per organization
    MAX_PUBLIC_AGENTS_PER_ORGANIZATION = 5

    # Organization ID field
    organization_id = serializers.UUIDField(
        required=True,
        help_text=_("ID of the organization to associate the agent with."),
    )

    # LLM ID field
    llm_id = serializers.UUIDField(
        required=True,
        help_text=_("ID of the LLM model to use with this agent."),
    )

    # Meta class for AgentCreateSerializer configuration
    class Meta:
        """Meta class for AgentCreateSerializer configuration.

        Attributes:
            model (Agent): The model class.
            fields (list): The fields to include in the serializer.
            extra_kwargs (dict): Additional field configurations.
        """

        # Model to use for the serializer
        model = Agent

        # Fields to include in the serializer
        fields = [
            "organization_id",
            "name",
            "description",
            "system_prompt",
            "is_public",
            "llm_id",
        ]

        # Extra kwargs
        extra_kwargs = {
            "name": {"required": True},
            "description": {"required": False},
            "system_prompt": {"required": True},
            "is_public": {"required": False},
        }

    # Validate the serializer data
    def validate(self, attrs):
        """Validate the serializer data.

        This method validates that:
        1. The user is a member of the specified organization.
        2. The user has not exceeded the maximum number of agents they can create.
           - Maximum 10 agents total per user
           - Within those 10, maximum 5 can be public agents
        3. The specified LLM exists and user has access to it.
        4. The LLM and agent must belong to the same organization and user.

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

        # Get the LLM ID
        llm_id = attrs.get("llm_id")

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

            # Try to get the LLM
            try:
                llm = LLM.objects.get(id=llm_id)

                # Check if the user has access to the LLM
                if llm.user and llm.user != user:
                    # Raise a validation error
                    raise serializers.ValidationError(
                        {
                            "llm_id": [
                                _("You do not have access to this LLM."),
                            ],
                        },
                    ) from None

                # Check if the LLM belongs to the same organization
                if llm.organization and llm.organization != organization:
                    # Raise a validation error
                    raise serializers.ValidationError(
                        {
                            "llm_id": [
                                _(
                                    "The LLM must belong to the same organization as the agent.",
                                ),
                            ],
                        },
                    ) from None

                # Store the LLM in attrs for later use
                attrs["llm"] = llm

            except LLM.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "llm_id": [
                            _("LLM not found."),
                        ],
                    },
                ) from None

            # Store the organization in attrs for later use
            attrs["organization"] = organization

            # Store the user in attrs for later use
            attrs["user"] = user

            # Remove the organization_id and llm_id from attrs as they're not fields in the Agent model
            del attrs["organization_id"]
            del attrs["llm_id"]

            # Check if the user has already created the maximum number of total agents
            total_agent_count = Agent.objects.filter(
                user=user,
            ).count()

            # Check if the user has reached the overall limit of 10 agents
            if total_agent_count >= self.MAX_AGENTS_PER_ORGANIZATION:
                # Raise a validation error
                raise serializers.ValidationError(
                    {
                        "non_field_errors": [
                            _("You can only create a maximum of 10 agents in total."),
                        ],
                    },
                ) from None

            # Check if the agent is public
            is_public = attrs.get("is_public", False)

            # If creating a public agent, check the public agent limit
            if is_public:
                # Count the user's existing public agents
                public_agent_count = Agent.objects.filter(
                    user=user,
                    is_public=True,
                ).count()

                # Check if the user has reached the limit for public agents
                if public_agent_count >= self.MAX_PUBLIC_AGENTS_PER_ORGANIZATION:
                    # Raise a validation error
                    raise serializers.ValidationError(
                        {
                            "is_public": [
                                _("You can only create a maximum of 5 public agents."),
                            ],
                        },
                    ) from None

        except Organization.DoesNotExist:
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "organization_id": [
                        _("Organization not found."),
                    ],
                },
            ) from None

        # Return the validated attributes
        return attrs

    # Create a new agent
    def create(self, validated_data):
        """Create a new agent.

        This method creates a new agent with the organization, user, and LLM set from validated data.

        Args:
            validated_data (dict): The validated data.

        Returns:
            Agent: The newly created agent.
        """

        # Get the organization from validated data
        organization = validated_data.pop("organization")

        # Get the user from validated data
        user = validated_data.pop("user")

        # Get the LLM from validated data
        llm = validated_data.pop("llm")

        # Return the created agent
        return Agent.objects.create(
            organization=organization,
            user=user,
            llm=llm,
            **validated_data,
        )


# Agent create success response serializer
class AgentCreateSuccessResponseSerializer(GenericResponseSerializer):
    """Agent creation success response serializer.

    This serializer defines the structure of the agent creation success response.
    It includes a status code and an agent object.

    Attributes:
        status_code (int): The status code of the response.
        agent (AgentResponseSchema): The newly created agent.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_201_CREATED,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Agent schema for swagger
    agent = serializers.SerializerMethodField(
        help_text=_("The newly created agent."),
        read_only=True,
    )

    # Get the agent representation
    @extend_schema_field(serializers.JSONField())
    def get_agent(self, obj) -> dict:
        """Get the agent representation.

        For documentation purposes only, not used in actual response.

        Args:
            obj: The agent object.

        Returns:
            dict: The agent representation.
        """

        # Return the agent representation
        return AgentResponseSchema(obj).data


# Agent creation error response serializer
class AgentCreateErrorResponseSerializer(GenericResponseSerializer):
    """Agent creation error response serializer (for schema).

    This serializer defines the structure of the wrapped validation error response
    as it would be formatted for documentation purposes.

    Attributes:
        status_code (int): The status code of the response.
        errors (AgentCreateErrorsDetailSerializer): The errors detail serializer.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Nested serializer defining the structure of the actual errors
    class AgentCreateErrorsDetailSerializer(serializers.Serializer):
        """Agent Creation Errors detail serializer.

        Attributes:
            organization_id (list): Errors related to the organization ID field.
            name (list): Errors related to the name field.
            system_prompt (list): Errors related to the system prompt field.
            is_public (list): Errors related to the is_public field.
            llm_id (list): Errors related to the LLM ID field.
            non_field_errors (list): Non-field specific errors.
        """

        # Organization ID field
        organization_id = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the organization ID field."),
        )

        # Name field
        name = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the name field."),
        )

        # System prompt field
        system_prompt = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the system prompt field."),
        )

        # Is public field
        is_public = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the is_public field."),
        )

        # LLM ID field
        llm_id = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the LLM ID field."),
        )

        # Non-field errors
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Non-field specific errors."),
        )

    # Define the 'errors' field containing the validation error details
    errors = AgentCreateErrorsDetailSerializer(
        help_text=_("Object containing validation errors."),
        read_only=True,
    )


# Agent authentication error response serializer
class AgentAuthErrorResponseSerializer(GenericResponseSerializer):
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
        default=_("Authentication credentials were not provided or are invalid."),
        read_only=True,
        help_text=_("Error message explaining the authentication failure."),
    )
