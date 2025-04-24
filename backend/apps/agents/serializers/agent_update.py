# Third-party imports
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.agents.models import Agent
from apps.agents.serializers.agent import AgentResponseSchema
from apps.common.serializers import GenericResponseSerializer
from apps.llms.models import LLM
from apps.tools.models import MCPServer

# Get the User model
User = get_user_model()


# Agent update serializer
class AgentUpdateSerializer(serializers.ModelSerializer):
    """Agent update serializer.

    This serializer handles updating existing AI agents. It validates
    that the agent exists and the user has permission to update it.

    Attributes:
        name (CharField): The name of the agent.
        description (TextField): A description of the agent.
        system_prompt (TextField): The system prompt used for the agent.
        llm_id (UUIDField): The ID of the LLM to associate the agent with.
        mcp_server_ids (ListField): List of MCP server IDs to associate with the agent.

    Meta:
        model (Agent): The Agent model.
        fields (list): The fields to include in the serializer.

    Raises:
        serializers.ValidationError: If the user doesn't have permission to update this agent.
        serializers.ValidationError: If the LLM doesn't exist or is not accessible.

    Returns:
        Agent: The updated agent instance.
    """

    # LLM ID field for looking up and assigning the LLM instance
    llm_id = serializers.UUIDField(
        required=False,
        help_text=_("ID of the LLM model to use with this agent."),
    )

    # MCP servers IDs field for looking up and assigning the MCP servers
    mcp_server_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text=_("List of MCP server IDs to associate with this agent."),
    )

    # Meta class for AgentUpdateSerializer configuration
    class Meta:
        """Meta class for AgentUpdateSerializer configuration.

        Attributes:
            model (Agent): The model class.
            fields (list): The fields to include in the serializer.
        """

        # Model to use for the serializer
        model = Agent

        # Fields to include in the serializer
        fields = [
            "name",
            "description",
            "system_prompt",
            "llm_id",
            "mcp_server_ids",
            "is_public",
        ]

        # Extra kwargs
        extra_kwargs = {
            "name": {"required": False},
            "description": {"required": False},
            "system_prompt": {"required": False},
            "is_public": {"required": False},
        }

    # Validate the serializer data
    def validate(self, attrs):
        """Validate the serializer data.

        This method validates that:
        1. The user has permission to update this agent.
        2. If a new LLM is specified, it exists and the user has access to it.
        3. If MCP servers are specified, they exist and the user has access to them.

        Args:
            attrs (dict): The attributes to validate.

        Returns:
            dict: The validated attributes.

        Raises:
            serializers.ValidationError: If validation fails.
        """

        # Get the user and agent from the context
        user = self.context["request"].user
        agent = self.context["agent"]

        # Validate user permissions
        self._validate_user_permissions(user, agent)

        # If a new LLM is specified
        if "llm_id" in attrs:
            # Validate the LLM
            attrs = self._validate_llm(attrs, user, agent)

        # If MCP servers are specified
        if "mcp_server_ids" in attrs:
            # Validate the MCP servers
            attrs = self._validate_mcp_servers(attrs, user, agent)

        # Return the validated data
        return attrs

    # Validate user permissions for updating the agent
    def _validate_user_permissions(self, user: User, agent: Agent):
        """Validate user permissions for updating the agent.

        Args:
            user: The user attempting to update the agent
            agent: The agent being updated

        Raises:
            serializers.ValidationError: If user doesn't have permission
        """

        # Check if the user owns this agent or is part of the organization
        if agent.user != user and (
            not agent.organization
            or (user not in agent.organization.members.all() and user != agent.organization.owner)
        ):
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        _("You do not have permission to update this agent."),
                    ],
                },
            )

    # Validate the LLM specified in the request
    def _validate_llm(self, attrs: dict, user: User, agent: Agent) -> dict:
        """Validate the LLM specified in the request.

        Args:
            attrs (dict): The attributes to validate
            user: The user making the request
            agent: The agent being updated

        Returns:
            dict: Updated attributes with llm object

        Raises:
            serializers.ValidationError: If LLM validation fails
        """

        # Get the LLM ID from the attributes
        llm_id = attrs["llm_id"]

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
                )

            # Check if the LLM belongs to the same organization
            if agent.organization and llm.organization and agent.organization != llm.organization:
                # Raise a validation error
                raise serializers.ValidationError(
                    {
                        "llm_id": [
                            _(
                                "The LLM must belong to the same organization as the agent.",
                            ),
                        ],
                    },
                )

            # Store the LLM in attrs for later use
            attrs["llm"] = llm

            # Remove the llm_id from attrs as it's not a field in the Agent model
            del attrs["llm_id"]

        except LLM.DoesNotExist:
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "llm_id": [
                        _("LLM not found."),
                    ],
                },
            ) from None

        return attrs

    # Validate the MCP servers specified in the request
    def _validate_mcp_servers(self, attrs: dict, user: User, agent: Agent) -> dict:
        """Validate the MCP servers specified in the request.

        Args:
            attrs (dict): The attributes to validate
            user: The user making the request
            agent: The agent being updated

        Returns:
            dict: Updated attributes with mcp_servers list

        Raises:
            serializers.ValidationError: If MCP server validation fails
        """

        # Get the MCP server IDs from the attributes
        mcp_server_ids = attrs["mcp_server_ids"]

        # Initialize an empty list to store the MCP servers
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

                # Check if the MCP server belongs to the same organization as the agent
                if agent.organization and mcp_server.organization and agent.organization != mcp_server.organization:
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

                # Add the MCP server to the list
                mcp_servers.append(mcp_server)

            except MCPServer.DoesNotExist:
                # Raise a validation error
                raise serializers.ValidationError(
                    {
                        "mcp_server_ids": [
                            _("MCP server with ID: {} not found.").format(mcp_server_id),
                        ],
                    },
                ) from None

        # Store the MCP servers in attrs for later use
        attrs["mcp_servers"] = mcp_servers

        # Remove the mcp_server_ids from attrs as it's not a field in the Agent model
        del attrs["mcp_server_ids"]

        # Return the updated attributes
        return attrs

    # Update the agent with the validated data
    def update(self, instance, validated_data):
        """Update the agent with the validated data.

        Args:
            instance (Agent): The existing agent instance.
            validated_data (dict): The validated data.

        Returns:
            Agent: The updated agent instance.
        """

        # Extract MCP servers from validated data if present
        mcp_servers = validated_data.pop("mcp_servers", None)

        # Update the agent with the validated data
        for key, value in validated_data.items():
            setattr(instance, key, value)

        # Save the agent
        instance.save()

        # If MCP servers were provided, update the many-to-many relationship
        if mcp_servers is not None:
            # Clear existing MCP servers
            instance.mcp_servers.clear()

            # Add the new MCP servers
            instance.mcp_servers.add(*mcp_servers)

        # Return the updated agent
        return instance


# Agent update success response serializer
class AgentUpdateSuccessResponseSerializer(GenericResponseSerializer):
    """Agent update success response serializer.

    This serializer defines the structure of the agent update success response.
    It includes a status code and an agent object.

    Attributes:
        status_code (int): The status code of the response.
        agent (AgentResponseSchema): The updated agent with detailed organization, user, and LLM information.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Agent data
    agent = AgentResponseSchema(
        help_text=_(
            "The updated agent with detailed organization, user, and LLM information.",
        ),
    )


# Agent update error response serializer
class AgentUpdateErrorResponseSerializer(GenericResponseSerializer):
    """Agent update error response serializer.

    This serializer defines the structure of the agent update error response.
    It includes a status code and error details.

    Attributes:
        status_code (int): The status code of the response.
        errors (AgentUpdateErrorsDetailSerializer): The detailed error serializer.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Nested serializer defining the structure of the actual errors
    class AgentUpdateErrorsDetailSerializer(serializers.Serializer):
        """Agent Update Errors detail serializer.

        Attributes:
            name (list): Errors related to the name field.
            description (list): Errors related to the description field.
            system_prompt (list): Errors related to the system prompt field.
            llm_id (list): Errors related to the LLM ID field.
            non_field_errors (list): Non-field specific errors.
        """

        # Name field
        name = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the name field."),
        )

        # Description field
        description = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the description field."),
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
    errors = AgentUpdateErrorsDetailSerializer(
        help_text=_("Validation errors for the agent update request."),
    )


# Agent not found error response serializer
class AgentNotFoundErrorResponseSerializer(GenericResponseSerializer):
    """Agent not found error response serializer.

    This serializer defines the structure of the agent not found error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response (404 Not Found).
        error (str): An error message explaining that the agent was not found.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_404_NOT_FOUND,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("Agent not found."),
        read_only=True,
        help_text=_("Error message explaining that the agent was not found."),
    )


# Agent auth error response serializer
class AgentAuthErrorResponseSerializer(GenericResponseSerializer):
    """Agent auth error response serializer.

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
class AgentPermissionDeniedResponseSerializer(GenericResponseSerializer):
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
        default=_("You do not have permission to update this agent."),
        read_only=True,
        help_text=_("Error message explaining the permission denial."),
    )
