# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Project imports
from apps.agents.serializers.llm import LLMSerializer
from apps.common.serializers import GenericResponseSerializer


# LLM list response serializer
class LLMListResponseSerializer(GenericResponseSerializer):
    """LLM list response serializer.

    This serializer defines the structure of the LLM list response.
    It includes a status code and a list of LLMs.

    Attributes:
        status_code (int): The status code of the response.
        llms (List[LLMSerializer]): List of LLM serializers.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # LLMs serializer
    llms = LLMSerializer(
        many=True,
        read_only=True,
        help_text=_("List of LLM configurations created by the user."),
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
