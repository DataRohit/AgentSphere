# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer
from apps.llms.models.choices import ApiType


# Model information serializer
class ModelInfoSerializer(serializers.Serializer):
    """Model information serializer.

    This serializer provides information about a specific model.

    Attributes:
        id (str): The model identifier.
        name (str): The human-readable name of the model.
    """

    # ID field
    id = serializers.CharField(
        help_text=_("The model identifier."),
        read_only=True,
    )

    # Name field
    name = serializers.CharField(
        help_text=_("The human-readable name of the model."),
        read_only=True,
    )


# LLM models success response serializer
class LLMModelsSuccessResponseSerializer(GenericResponseSerializer):
    """LLM models success response serializer.

    This serializer defines the structure of the LLM models success response.
    It includes a status code and a list of models.

    Attributes:
        status_code (int): The status code of the response.
        models (List[ModelInfoSerializer]): List of models with their IDs and names.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Models list
    models = ModelInfoSerializer(
        many=True,
        read_only=True,
        help_text=_("List of models with their IDs and names."),
    )


# LLM models invalid API type response serializer
class LLMModelsInvalidApiTypeResponseSerializer(GenericResponseSerializer):
    """LLM models invalid API type response serializer.

    This serializer defines the structure of the response when an invalid API type is provided.

    Attributes:
        status_code (int): The status code of the response.
        error (str): The error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("Invalid API type. Supported types: {}.").format(
            ", ".join([choice[0] for choice in ApiType.choices]),
        ),
        read_only=True,
        help_text=_("Error message."),
    )


# LLM models authentication error response serializer
class LLMModelsAuthErrorResponseSerializer(GenericResponseSerializer):
    """LLM models authentication error response serializer.

    This serializer defines the structure of the authentication error response.

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
        default=_("Authentication credentials were not provided or are invalid."),
        read_only=True,
        help_text=_("Error message."),
    )
