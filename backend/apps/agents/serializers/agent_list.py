# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Project imports
from apps.agents.serializers.agent import AgentSerializer
from apps.common.serializers import GenericResponseSerializer


# Agent list response serializer
class AgentListResponseSerializer(GenericResponseSerializer):
    """Agent list response serializer.

    This serializer defines the structure of the agent list response.
    It includes a status code and a list of agents.

    Attributes:
        status_code (int): The status code of the response.
        agents (List[AgentSerializer]): List of agent objects with detailed information.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Agent list
    agents = AgentSerializer(
        many=True,
        read_only=True,
        help_text=_(
            "List of agents with detailed information about organization, user, and LLM.",
        ),
    )


# Agent list me response serializer
class AgentListMeResponseSerializer(GenericResponseSerializer):
    """Agent list me response serializer.

    This serializer defines the structure of the response for the 'list/me' endpoint.
    It includes a status code and a list of agents created by the current user.

    Attributes:
        status_code (int): The status code of the response.
        agents (List[AgentSerializer]): List of agent objects created by the current user.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Agent list
    agents = AgentSerializer(
        many=True,
        read_only=True,
        help_text=_(
            "List of agents created by the current user with detailed information.",
        ),
    )


# Agent list not found error response serializer
class AgentListNotFoundResponseSerializer(GenericResponseSerializer):
    """Agent list not found error response serializer.

    This serializer defines the structure of the 404 Not Found error response
    when no agents are found matching the specified criteria.

    Attributes:
        status_code (int): The status code of the response (404 Not Found).
        error (str): An error message explaining why no agents were found.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_404_NOT_FOUND,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("No agents found matching the criteria."),
        read_only=True,
        help_text=_("Error message explaining why no agents were found."),
    )


# Missing required parameter error response serializer
class AgentListMissingParamResponseSerializer(GenericResponseSerializer):
    """Missing required parameter error response serializer.

    This serializer defines the structure of the 400 Bad Request error response
    when a required parameter is missing from the request.

    Attributes:
        status_code (int): The status code of the response (400 Bad Request).
        error (str): An error message explaining the missing parameter.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("Missing required parameter: organization_id"),
        read_only=True,
        help_text=_("Error message explaining the missing parameter."),
    )
