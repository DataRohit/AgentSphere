# Third-party imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers, status

# Project imports
from apps.agents.models import LLM, Agent
from apps.agents.serializers.agent import AgentResponseSchema
from apps.common.serializers import GenericResponseSerializer


# Agent update serializer
class AgentUpdateSerializer(serializers.ModelSerializer):
    """Agent update serializer.

    This serializer handles updating existing AI agents. Only the agent's creator
    can update the agent.

    Attributes:
        name (CharField): The name of the agent.
        description (TextField): A description of the agent.
        system_prompt (TextField): The system prompt used for the agent.
        is_public (BooleanField): Whether the agent is publicly visible.
        llm_id (UUIDField): The ID of the LLM to associate with the agent.

    Meta:
        model (Agent): The Agent model.
        fields (list): The fields that can be updated.
        extra_kwargs (dict): Additional field configurations.
    """

    # LLM ID field
    llm_id = serializers.UUIDField(
        required=False,
        help_text=_("ID of the LLM model to use with this agent."),
        write_only=True,
    )

    # Meta class for AgentUpdateSerializer configuration
    class Meta:
        """Meta class for AgentUpdateSerializer configuration.

        Attributes:
            model (Agent): The model class.
            fields (list): The fields that can be updated.
            extra_kwargs (dict): Additional field configurations.
        """

        # Model to use for the serializer
        model = Agent

        # Fields that can be updated
        fields = [
            "name",
            "description",
            "system_prompt",
            "is_public",
            "llm_id",
        ]

        # Extra kwargs
        extra_kwargs = {
            "name": {"required": False},
            "description": {"required": False},
            "system_prompt": {"required": False},
            "is_public": {"required": False},
        }

    # Validate the LLM ID
    def validate_llm_id(self, value):
        """Validate that the specified LLM exists and is accessible by the user.

        Args:
            value: The LLM ID value.

        Returns:
            UUID: The validated LLM ID.

        Raises:
            serializers.ValidationError: If validation fails.
        """

        # Get the agent instance being updated
        agent = self.instance

        try:
            # Try to get the LLM
            llm = LLM.objects.get(id=value)

            # Check if the user has access to the LLM
            if llm.user and llm.user != agent.user:
                raise serializers.ValidationError(
                    _("You do not have access to this LLM."),
                )

            # Check if the LLM belongs to the same organization
            if (
                llm.organization
                and agent.organization
                and llm.organization != agent.organization
            ):
                # Raise a validation error
                raise serializers.ValidationError(
                    _("The LLM must belong to the same organization as the agent."),
                )

        except LLM.DoesNotExist:
            # Error message
            error_message = _("LLM not found.")

            # Raise a validation error
            raise serializers.ValidationError(error_message) from None

        # Return the validated LLM ID
        return value

    # Update method
    def update(self, instance: Agent, validated_data: dict) -> Agent:
        """Update the agent instance.

        Args:
            instance: The agent instance to update.
            validated_data: The validated data to update with.

        Returns:
            Agent: The updated agent instance.
        """

        # Handle the LLM ID if provided
        llm_id = validated_data.pop("llm_id", None)

        # If the LLM ID is provided
        if llm_id:
            try:
                # Try to get the LLM
                llm = LLM.objects.get(id=llm_id)

                # Update the agent's LLM
                instance.llm = llm

            except LLM.DoesNotExist:
                # Error message
                error_message = _("LLM not found.")

                # Raise a validation error
                raise serializers.ValidationError(error_message) from None

        # Update the instance with the rest of the validated data
        return super().update(instance, validated_data)


# Agent update success response serializer
class AgentUpdateSuccessResponseSerializer(GenericResponseSerializer):
    """Agent update success response serializer.

    This serializer defines the structure of the agent update success response.
    It includes a status code and an agent object.

    Attributes:
        status_code (int): The status code of the response.
        agent (dict): The updated agent data.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Agent serializer
    agent = serializers.SerializerMethodField(
        help_text=_("The updated agent."),
    )

    # Get the agent representation
    @extend_schema_field(serializers.JSONField())
    def get_agent(self, obj: Agent) -> dict:
        """Get the agent representation.

        For documentation purposes only, not used in actual response.

        Args:
            obj: The agent object.

        Returns:
            dict: The agent representation.
        """

        # Return the agent representation
        return AgentResponseSchema(obj).data


# Agent update error response serializer
class AgentUpdateErrorResponseSerializer(GenericResponseSerializer):
    """Agent update error response serializer (for schema).

    This serializer defines the structure of the wrapped validation error response
    as it would be formatted for documentation purposes.

    Attributes:
        status_code (int): The status code of the response.
        errors (AgentUpdateErrorsDetailSerializer): The errors detail serializer.
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
            system_prompt (list): Errors related to the system prompt field.
            is_public (list): Errors related to the is_public field.
            llm_id (list): Errors related to the LLM ID field.
            non_field_errors (list): Non-field specific errors.
        """

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
    errors = AgentUpdateErrorsDetailSerializer(
        help_text=_("Object containing validation errors."),
        read_only=True,
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


# Agent not found error response serializer
class AgentNotFoundResponseSerializer(GenericResponseSerializer):
    """Agent not found error response serializer.

    This serializer defines the structure of the 404 Not Found error response
    when the specified agent cannot be found.

    Attributes:
        status_code (int): The status code of the response (404 Not Found).
        error (str): An error message explaining why the agent wasn't found.
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
        help_text=_("Error message explaining why the agent wasn't found."),
    )
