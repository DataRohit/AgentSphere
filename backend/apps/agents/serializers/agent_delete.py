# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer


# Agent delete success response serializer
class AgentDeleteSuccessResponseSerializer(GenericResponseSerializer):
    """Agent delete success response serializer.

    This serializer defines the structure of the agent delete success response.
    It includes a status code and a success message.

    Attributes:
        status_code (int): The status code of the response.
        message (str): A success message.
    """

    # Agent delete success message response serializer
    class AgentDeleteSuccessMessageResponseSerializer(serializers.Serializer):
        """Agent delete success message response serializer.

        Attributes:
            message (str): A success message.
        """

        # Message
        message = serializers.CharField(
            default=_("Agent deleted successfully."),
            read_only=True,
            help_text=_("Success message confirming the agent was deleted."),
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Success message
    agent = AgentDeleteSuccessMessageResponseSerializer(
        read_only=True,
        help_text=_("Success message confirming the agent was deleted."),
    )


# Permission denied error response serializer for delete
class AgentDeletePermissionDeniedResponseSerializer(GenericResponseSerializer):
    """Permission denied error response serializer for delete operation.

    This serializer defines the structure of the permission denied error response
    when attempting to delete an agent.

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
        default=_("You do not have permission to delete this agent."),
        read_only=True,
        help_text=_("Error message explaining the permission denial."),
    )


# Agent not found error response serializer for delete
class AgentDeleteNotFoundResponseSerializer(GenericResponseSerializer):
    """Agent not found error response serializer for delete operation.

    This serializer defines the structure of the 404 Not Found error response
    when the specified agent to delete cannot be found.

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
        help_text=_("Error message explaining that the agent to delete wasn't found."),
    )
