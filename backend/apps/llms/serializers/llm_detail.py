# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer
from apps.llms.serializers.llm import LLMResponseSchema


# LLM detail success response serializer
class LLMDetailSuccessResponseSerializer(GenericResponseSerializer):
    """LLM detail success response serializer.

    This serializer defines the structure of the LLM detail success response.
    It includes a status code and an LLM object.

    Attributes:
        status_code (int): The status code of the response.
        llm (LLMResponseSchema): The LLM details with organization and user information.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # LLM data
    llm = LLMResponseSchema(
        help_text=_("The LLM details with organization and user information."),
        read_only=True,
    )


# LLM detail not found error response serializer
class LLMDetailNotFoundResponseSerializer(GenericResponseSerializer):
    """LLM detail not found error response serializer.

    This serializer defines the structure of the 404 Not Found error response
    when the specified LLM configuration cannot be found.

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
        default=_("LLM configuration not found."),
        read_only=True,
        help_text=_("Error message explaining why the LLM configuration wasn't found."),
    )


# LLM detail permission denied error response serializer
class LLMDetailPermissionDeniedResponseSerializer(GenericResponseSerializer):
    """LLM detail permission denied error response serializer.

    This serializer defines the structure of the 403 Forbidden error response
    when the user does not have permission to view the LLM configuration.

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
        default=_("You do not have permission to view this LLM configuration."),
        read_only=True,
        help_text=_("Error message explaining the permission denial."),
    )
