# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Project imports
from apps.agents.serializers.agent import AgentResponseSchema
from apps.common.serializers import GenericResponseSerializer


# Agent detail success response serializer
class AgentDetailSuccessResponseSerializer(GenericResponseSerializer):
    """Agent detail success response serializer.

    This serializer defines the structure of the agent detail success response.
    It includes a status code and an agent object.

    Attributes:
        status_code (int): The status code of the response.
        agent (AgentResponseSchema): The agent details with organization, user, and LLM information.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Agent data
    agent = AgentResponseSchema(
        help_text=_("The agent details with organization, user, and LLM information."),
        read_only=True,
    )


# Agent detail not found error response serializer
class AgentDetailNotFoundResponseSerializer(GenericResponseSerializer):
    """Agent detail not found error response serializer.

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


# Agent detail permission denied error response serializer
class AgentDetailPermissionDeniedResponseSerializer(GenericResponseSerializer):
    """Agent detail permission denied error response serializer.

    This serializer defines the structure of the 403 Forbidden error response
    when the user does not have permission to view the agent.

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
        default=_("You do not have permission to view this agent."),
        read_only=True,
        help_text=_("Error message explaining the permission denial."),
    )
