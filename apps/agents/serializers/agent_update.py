# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Project imports
from apps.agents.models import Agent
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
        type (CharField): The type or category of the agent.
        system_prompt (TextField): The system prompt used for the agent.
        is_public (BooleanField): Whether the agent is publicly visible.

    Meta:
        model (Agent): The Agent model.
        fields (list): The fields that can be updated.
        extra_kwargs (dict): Additional field configurations.
    """

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
            "type",
            "system_prompt",
            "is_public",
        ]

        # Extra kwargs
        extra_kwargs = {
            "name": {"required": False},
            "description": {"required": False},
            "type": {"required": False},
            "system_prompt": {"required": False},
            "is_public": {"required": False},
        }


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
    agent = AgentResponseSchema(
        help_text=_("The updated agent."),
        read_only=True,
    )


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
    )

    # Nested serializer defining the structure of the actual errors
    class AgentUpdateErrorsDetailSerializer(serializers.Serializer):
        """Agent Update Errors detail serializer.

        Attributes:
            name (list): Errors related to the name field.
            type (list): Errors related to the type field.
            system_prompt (list): Errors related to the system prompt field.
            is_public (list): Errors related to the is_public field.
            non_field_errors (list): Non-field specific errors.
        """

        # Name field
        name = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the name field."),
        )

        # Type field
        type = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the type field."),
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

        # Non-field errors
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Non-field specific errors."),
        )

    # Define the 'errors' field containing the validation error details
    errors = AgentUpdateErrorsDetailSerializer(
        help_text=_("Object containing validation errors."),
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
