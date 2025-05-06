# Third-party imports
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.agents.models import Agent
from apps.agents.serializers.agent import AgentResponseSchema
from apps.common.serializers import GenericResponseSerializer
from apps.llms.models import LLM
from apps.organization.models import Organization
from apps.tools.models import MCPServer

# Get the User model
User = get_user_model()


# Agent creation serializer
class AgentCreateSerializer(serializers.ModelSerializer):
    """Agent creation serializer.

    This serializer handles the creation of new AI agents. It validates that
    the user is a member of the specified organization and has not exceeded
    the maximum number of agents they can create per organization.

    Attributes:
        organization_id (UUIDField): The ID of the organization to associate the agent with.
        name (CharField): The name of the agent.
        description (TextField): A description of the agent.
        system_prompt (TextField): The system prompt used for the agent.
        llm_id (UUIDField): The ID of the LLM to associate the agent with.
        mcp_server_ids (ListField): List of MCP server IDs to associate with the agent.

    Meta:
        model (Agent): The Agent model.
        fields (list): The fields to include in the serializer.
        extra_kwargs (dict): Additional field configurations.

    Raises:
        serializers.ValidationError: If user is not a member of the organization.
        serializers.ValidationError: If user has exceeded the maximum number of agents per organization.
        serializers.ValidationError: If LLM doesn't exist or user doesn't have access.

    Returns:
        Agent: The newly created agent instance.
    """

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

    # MCP servers IDs field
    mcp_server_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text=_("List of MCP server IDs to associate with this agent."),
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
            "llm_id",
            "mcp_server_ids",
        ]

        # Extra kwargs
        extra_kwargs = {
            "name": {"required": True},
            "description": {"required": False},
            "system_prompt": {"required": True},
        }

    # Validate the serializer data
    def validate(self, attrs: dict) -> dict:
        """Validate the serializer data.

        This method validates that:
        1. The user is a member of the specified organization.
        2. The user has not exceeded the maximum number of agents they can create per organization.
        3. The specified LLM exists and user has access to it.
        4. The LLM and agent must belong to the same organization and user.
        5. If MCP servers are specified, they exist and the user has access to them.

        Args:
            attrs (dict): The attributes to validate.

        Returns:
            dict: The validated attributes.

        Raises:
            serializers.ValidationError: If validation fails.
        """

        # Get the user from the context
        user = self.context["request"].user

        # Validate organization
        organization_id = attrs.get("organization_id")
        organization = self._validate_organization(organization_id, user)

        # Store the organization in attrs for later use
        attrs["organization"] = organization

        # Validate user's agent count for the organization
        self._validate_agent_count(user, organization)

        # Validate LLM
        llm_id = attrs.get("llm_id")
        llm = self._validate_llm(llm_id, user, organization)

        # Store the LLM in attrs for later use
        attrs["llm"] = llm

        # If MCP servers are specified
        mcp_server_ids = attrs.get("mcp_server_ids")
        if mcp_server_ids:
            # Validate the MCP servers
            mcp_servers = self._validate_mcp_servers(mcp_server_ids, user, organization)

            # Store the MCP servers in attrs for later use
            attrs["mcp_servers"] = mcp_servers

        # Store the user in attrs for later use
        attrs["user"] = user

        # Remove fields that aren't in the Agent model
        del attrs["organization_id"]
        del attrs["llm_id"]

        # If MCP server IDs are present
        if "mcp_server_ids" in attrs:
            # Remove the MCP server IDs from attrs
            attrs.pop("mcp_server_ids")

        # Return the validated attributes
        return attrs

    # Validate the organization
    def _validate_organization(self, organization_id: str, user: User) -> Organization:
        """Validate the organization exists and user is a member.

        Args:
            organization_id: UUID of the organization
            user: The user making the request

        Returns:
            Organization: The validated organization

        Raises:
            serializers.ValidationError: If organization doesn't exist or user is not a member
        """

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

        # If the organization doesn't exist
        except Organization.DoesNotExist:
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "organization_id": [
                        _("Organization not found."),
                    ],
                },
            ) from None

        # Return the organization
        return organization

    # Validate the agent count
    def _validate_agent_count(self, user: User, organization: Organization) -> None:
        """Validate user hasn't exceeded the maximum number of agents per organization.

        Args:
            user: The user making the request
            organization: The organization to check against

        Raises:
            serializers.ValidationError: If user has exceeded maximum agents limit
        """

        # Get the number of agents the user has created in the organization
        user_agents_count = Agent.objects.filter(
            organization=organization,
            user=user,
        ).count()

        # If the user has exceeded the maximum number of agents per organization
        if user_agents_count >= Agent.MAX_AGENTS_PER_USER_PER_ORGANIZATION:
            # Set the error message
            error_message = f"You can only create a maximum of {Agent.MAX_AGENTS_PER_USER_PER_ORGANIZATION} agents per organization."  # noqa: E501

            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        error_message,
                    ],
                },
            ) from None

    # Validate the LLM
    def _validate_llm(self, llm_id: str, user: User, organization: Organization) -> LLM:
        """Validate the LLM exists and user has access to it.

        Args:
            llm_id: UUID of the LLM
            user: The user making the request
            organization: The organization the agent belongs to

        Returns:
            LLM: The validated LLM

        Raises:
            serializers.ValidationError: If LLM doesn't exist or user doesn't have access
        """

        try:
            # Try to get the LLM
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

        # If the LLM doesn't exist
        except LLM.DoesNotExist:
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "llm_id": [
                        _("LLM not found."),
                    ],
                },
            ) from None

        # Return the LLM
        return llm

    # Validate the MCP servers
    def _validate_mcp_servers(self, mcp_server_ids: list, user: User, organization: Organization) -> list:
        """Validate the MCP servers exist and user has access to them.

        Args:
            mcp_server_ids: List of MCP server UUIDs
            user: The user making the request
            organization: The organization the agent belongs to

        Returns:
            list: List of validated MCP server objects

        Raises:
            serializers.ValidationError: If MCP servers don't exist or user doesn't have access
        """

        # Initialize an empty list to store the validated MCP servers
        mcp_servers = []

        # Iterate over the MCP server IDs
        for mcp_server_id in mcp_server_ids:
            try:
                # Try to get the MCP server
                mcp_server = MCPServer.objects.get(id=mcp_server_id)

                # Check if the user has access to the MCP server
                if mcp_server.user != user and (
                    not mcp_server.organization
                    or (user not in mcp_server.organization.members.all() and user != mcp_server.organization.owner)
                ):
                    # Raise a validation error
                    raise serializers.ValidationError(
                        {
                            "mcp_server_ids": [
                                _("You do not have access to MCP server with ID: {}.").format(mcp_server_id),
                            ],
                        },
                    )

                # Check if the MCP server belongs to the same organization
                if mcp_server.organization and mcp_server.organization != organization:
                    # Raise a validation error
                    raise serializers.ValidationError(
                        {
                            "mcp_server_ids": [
                                _(
                                    "MCP server with ID: {} must belong to the same organization as the agent.",
                                ).format(mcp_server_id),
                            ],
                        },
                    )

                # Add the MCP server to the list of validated MCP servers
                mcp_servers.append(mcp_server)

            # If the MCP server doesn't exist
            except MCPServer.DoesNotExist:
                # Raise a validation error
                raise serializers.ValidationError(
                    {
                        "mcp_server_ids": [
                            _("MCP server with ID: {} not found.").format(mcp_server_id),
                        ],
                    },
                ) from None

        # Return the list of validated MCP servers
        return mcp_servers

    # Create method to create a new agent
    def create(self, validated_data: dict) -> Agent:
        """Create a new agent with the validated data.

        Args:
            validated_data (dict): The validated data.

        Returns:
            Agent: The newly created agent.
        """

        # Extract MCP servers from validated data if present
        mcp_servers = validated_data.pop("mcp_servers", None)

        # Create a new agent with the validated data
        agent = Agent.objects.create(**validated_data)

        # If MCP servers were provided
        if mcp_servers:
            # Add the MCP servers to the agent
            agent.mcp_servers.add(*mcp_servers)

        # Save the agent
        agent.save()

        # Return the created agent
        return agent


# Agent creation success response serializer
class AgentCreateSuccessResponseSerializer(GenericResponseSerializer):
    """Agent creation success response serializer.

    This serializer defines the structure of the agent creation success response.
    It includes a status code and an agent object.

    Attributes:
        status_code (int): The status code of the response.
        agent (AgentResponseSchema): The newly created agent with detailed organization, user, and LLM information.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_201_CREATED,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Agent data
    agent = AgentResponseSchema(
        help_text=_(
            "The newly created agent with detailed organization, user, and LLM information.",
        ),
    )


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

        # LLM ID field
        llm_id = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the LLM ID field."),
        )

        # MCP server IDs field
        mcp_server_ids = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the MCP server IDs field."),
        )

        # Non-field errors
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Non-field specific errors."),
        )

    # Define the 'errors' field containing the validation error details
    errors = AgentCreateErrorsDetailSerializer(
        help_text=_("Validation errors for the agent creation request."),
    )


# Authentication error response serializer
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
        default=_("Authentication credentials were not provided."),
        read_only=True,
        help_text=_("Error message explaining the authentication failure."),
    )
