# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer


# LLM delete success response serializer
class LLMDeleteSuccessResponseSerializer(GenericResponseSerializer):
    """LLM delete success response serializer.

    This serializer defines the structure of the LLM delete success response.
    It includes a status code and a success message.

    Attributes:
        status_code (int): The status code of the response.
        message (str): A success message.
    """

    # LLM delete success message response serializer
    class LLMDeleteSuccessMessageResponseSerializer(serializers.Serializer):
        """LLM delete success message response serializer.

        Attributes:
            message (str): A success message.
        """

        # Message
        message = serializers.CharField(
            default=_("LLM deleted successfully."),
            read_only=True,
            help_text=_("Success message confirming the LLM was deleted."),
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Success message
    llm = LLMDeleteSuccessMessageResponseSerializer(
        read_only=True,
        help_text=_("Success message confirming the LLM was deleted."),
    )


# Permission denied error response serializer for delete
class LLMDeletePermissionDeniedResponseSerializer(GenericResponseSerializer):
    """Permission denied error response serializer for delete operation.

    This serializer defines the structure of the permission denied error response
    when attempting to delete an LLM.

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
        default=_("You do not have permission to delete this LLM."),
        read_only=True,
        help_text=_("Error message explaining the permission denial."),
    )


# LLM not found error response serializer for delete
class LLMDeleteNotFoundResponseSerializer(GenericResponseSerializer):
    """LLM not found error response serializer for delete operation.

    This serializer defines the structure of the 404 Not Found error response
    when the specified LLM to delete cannot be found.

    Attributes:
        status_code (int): The status code of the response (404 Not Found).
        error (str): An error message explaining why the LLM wasn't found.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_404_NOT_FOUND,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("LLM not found."),
        read_only=True,
        help_text=_("Error message explaining that the LLM to delete wasn't found."),
    )


# LLM has associated agents error response serializer
class LLMHasAgentsResponseSerializer(GenericResponseSerializer):
    """LLM has associated agents error response serializer.

    This serializer defines the structure of the error response when
    attempting to delete an LLM that has associated agents.

    Attributes:
        status_code (int): The status code of the response (400 Bad Request).
        error (str): An error message explaining that the LLM has associated agents.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_(
            "Cannot delete LLM because it is associated with one or more agents.",
        ),
        read_only=True,
        help_text=_("Error message explaining that the LLM has associated agents."),
    )
