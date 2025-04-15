# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer
from apps.llms.serializers.llm import LLMSerializer


# LLM list response serializer
class LLMListResponseSerializer(GenericResponseSerializer):
    """LLM list response serializer.

    This serializer defines the structure of the LLM list response.
    It includes a status code and a list of LLMs.

    Attributes:
        status_code (int): The status code of the response.
        llms (List[LLMSerializer]): List of LLM objects with detailed information.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # LLM list
    llms = LLMSerializer(
        many=True,
        read_only=True,
        help_text=_(
            "List of LLM configurations with detailed information about organization and user.",
        ),
    )


# LLM list me response serializer
class LLMListMeResponseSerializer(GenericResponseSerializer):
    """LLM list me response serializer.

    This serializer defines the structure of the response for the 'llm/list/me' endpoint.
    It includes a status code and a list of LLMs created by the current user.

    Attributes:
        status_code (int): The status code of the response.
        llms (List[LLMSerializer]): List of LLM objects created by the current user.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # LLM list
    llms = LLMSerializer(
        many=True,
        read_only=True,
        help_text=_(
            "List of LLM configurations created by the current user with detailed information.",
        ),
    )


# LLM list not found error response serializer
class LLMListNotFoundResponseSerializer(GenericResponseSerializer):
    """LLM list not found error response serializer.

    This serializer defines the structure of the 404 Not Found error response
    when no LLMs are found matching the specified criteria.

    Attributes:
        status_code (int): The status code of the response (404 Not Found).
        error (str): An error message explaining why no LLMs were found.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_404_NOT_FOUND,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("No LLM configurations found matching the criteria."),
        read_only=True,
        help_text=_("Error message explaining why no LLMs were found."),
    )


# Missing required parameter error response serializer
class LLMListMissingParamResponseSerializer(GenericResponseSerializer):
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
