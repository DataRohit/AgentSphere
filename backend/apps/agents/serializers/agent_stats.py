# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.agents.models import Agent
from apps.agents.serializers.agent import AgentUserSerializer
from apps.common.serializers import GenericResponseSerializer


# Agent stats serializer
class AgentStatsSerializer(serializers.ModelSerializer):
    """Serializer for agent statistics.

    This serializer defines the structure of the agent statistics response.
    It includes basic agent information, user information, and a count field.

    Attributes:
        id (UUIDField): The ID of the agent.
        name (CharField): The name of the agent.
        description (CharField): The description of the agent.
        user (AgentUserSerializer): The user who created the agent.
        count (IntegerField): The count value for the agent.
    """

    # User field
    user = AgentUserSerializer(read_only=True)

    # Count field
    count = serializers.IntegerField(
        read_only=True,
        help_text=_("Count value for the agent."),
    )

    class Meta:
        """Meta class for AgentStatsSerializer configuration.

        Attributes:
            model (Agent): The model class.
            fields (list): The fields to include in the serializer.
        """

        # Model to use for the serializer
        model = Agent

        # Fields to include in the serializer
        fields = [
            "id",
            "name",
            "description",
            "user",
            "count",
        ]


# Most used agents success response serializer
class MostUsedAgentsSuccessResponseSerializer(GenericResponseSerializer):
    """Serializer for successful most used agents response.

    This serializer defines the structure of the most used agents success response.
    It includes a status code and a list of agents with their usage counts.

    Attributes:
        status_code (int): The status code of the response.
        agents (list): A list of agents with their usage counts.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Agents list
    agents = serializers.ListField(
        child=AgentStatsSerializer(),
        read_only=True,
        help_text=_("List of most used agents with their usage counts."),
    )


# Most active agents success response serializer
class MostActiveAgentsSuccessResponseSerializer(GenericResponseSerializer):
    """Serializer for successful most active agents response.

    This serializer defines the structure of the most active agents success response.
    It includes a status code and a list of agents with their activity counts.

    Attributes:
        status_code (int): The status code of the response.
        agents (list): A list of agents with their activity counts.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Agents list
    agents = serializers.ListField(
        child=AgentStatsSerializer(),
        read_only=True,
        help_text=_("List of most active agents with their activity counts."),
    )


# Agent stats auth error response serializer
class AgentStatsAuthErrorResponseSerializer(GenericResponseSerializer):
    """Serializer for agent stats authentication error response.

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
        help_text=_("Error message."),
    )
