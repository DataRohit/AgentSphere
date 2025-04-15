# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer
from apps.llms.models import LLM, ApiType, GoogleGeminiModel, OllamaModel
from apps.llms.serializers.llm import LLMResponseSchema


# LLM update serializer
class LLMUpdateSerializer(serializers.ModelSerializer):
    """LLM update serializer.

    This serializer handles updating existing LLM configurations. Only the LLM's creator
    can update the LLM.

    Attributes:
        api_type (CharField): The API provider type (Ollama or Gemini).
        model (CharField): The specific model name.
        api_key (CharField): API key for authentication (required for Gemini, not for Ollama).
        max_tokens (PositiveIntegerField): Maximum tokens for generation.

    Meta:
        model (LLM): The LLM model.
        fields (list): The fields that can be updated.
        extra_kwargs (dict): Additional field configurations.
    """

    # Meta class for LLMUpdateSerializer configuration
    class Meta:
        """Meta class for LLMUpdateSerializer configuration.

        Attributes:
            model (LLM): The model class.
            fields (list): The fields that can be updated.
            extra_kwargs (dict): Additional field configurations.
        """

        # Model to use for the serializer
        model = LLM

        # Fields that can be updated
        fields = [
            "api_type",
            "model",
            "api_key",
            "max_tokens",
        ]

        # Extra kwargs
        extra_kwargs = {
            "api_type": {"required": False},
            "model": {"required": False},
            "api_key": {"required": False, "write_only": True},
            "max_tokens": {"required": False},
        }

    # Validate the API type
    def validate_api_type(self, value):
        """Validate the API type.

        Args:
            value: The API type value.

        Returns:
            str: The validated API type.

        Raises:
            serializers.ValidationError: If the API type is invalid.
        """

        # Check if the API type is valid
        if value not in [choice[0] for choice in ApiType.choices]:
            # Error message
            error_message = _("Invalid API type.")

            # Raise a validation error
            raise serializers.ValidationError(error_message) from None

        # Return the validated API type
        return value

    # Validate the model
    def validate(self, attrs: dict) -> dict:
        """Validate the data before updating.

        This method validates that:
        1. The model is compatible with the selected API type.
        2. API key is provided when using Gemini API type.

        Args:
            attrs (dict): The attributes to validate.

        Returns:
            dict: The validated attributes.

        Raises:
            serializers.ValidationError: If validation fails.
        """

        # Get the submitted values or use the current instance values
        api_type = attrs.get(
            "api_type",
            self.instance.api_type if self.instance else None,
        )
        model = attrs.get("model", self.instance.model if self.instance else None)
        api_key = attrs.get("api_key")

        # If both api_type and model are provided, validate their compatibility
        if api_type and model:
            # Validate model selection for Ollama
            if api_type == ApiType.OLLAMA:
                # Check if the model is in the Ollama model choices
                if model not in [choice[0] for choice in OllamaModel.choices]:
                    # Raise a validation error
                    raise serializers.ValidationError(
                        {
                            "model": [
                                _(
                                    "Invalid model for Ollama API. Choose from: {}",
                                ).format(
                                    ", ".join(
                                        [choice[0] for choice in OllamaModel.choices],
                                    ),
                                ),
                            ],
                        },
                    )

            # Validate model selection for Gemini
            elif api_type == ApiType.GEMINI:
                # Check if the model is in the Gemini model choices
                if model not in [choice[0] for choice in GoogleGeminiModel.choices]:
                    # Raise a validation error
                    raise serializers.ValidationError(
                        {
                            "model": [
                                _(
                                    "Invalid model for Gemini API. Choose from: {}",
                                ).format(
                                    ", ".join(
                                        [choice[0] for choice in GoogleGeminiModel.choices],
                                    ),
                                ),
                            ],
                        },
                    )

                # If API type is Gemini and api_key is not provided check if there's an existing API key
                if not api_key and not self.instance.get_api_key():
                    # Raise a validation error
                    raise serializers.ValidationError(
                        {
                            "api_key": [_("API key is required for Gemini API.")],
                        },
                    )

        # If changing to Gemini but not providing a key
        elif api_type == ApiType.GEMINI and not api_key and not self.instance.get_api_key():
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "api_key": [_("API key is required for Gemini API.")],
                },
            )

        # Return the validated attributes
        return attrs


# LLM update success response serializer
class LLMUpdateSuccessResponseSerializer(GenericResponseSerializer):
    """LLM update success response serializer.

    This serializer defines the structure of the LLM update success response.
    It includes a status code and an LLM object.

    Attributes:
        status_code (int): The status code of the response.
        llm (LLMResponseSchema): The updated LLM with detailed organization and user information.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # LLM data
    llm = LLMResponseSchema(
        help_text=_("The updated LLM with detailed organization and user information."),
        read_only=True,
    )


# LLM update error response serializer
class LLMUpdateErrorResponseSerializer(GenericResponseSerializer):
    """LLM update error response serializer (for schema).

    This serializer defines the structure of the wrapped validation error response
    as it would be formatted for documentation purposes.

    Attributes:
        status_code (int): The status code of the response.
        errors (LLMUpdateErrorsDetailSerializer): The errors detail serializer.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Nested serializer defining the structure of the actual errors
    class LLMUpdateErrorsDetailSerializer(serializers.Serializer):
        """LLM Update Errors detail serializer.

        Attributes:
            api_type (list): Errors related to the API type field.
            model (list): Errors related to the model field.
            api_key (list): Errors related to the API key field.
            max_tokens (list): Errors related to the max tokens field.
            non_field_errors (list): Non-field specific errors.
        """

        # API type field
        api_type = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the API type field."),
        )

        # Model field
        model = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the model field."),
        )

        # API key field
        api_key = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the API key field."),
        )

        # Max tokens field
        max_tokens = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the max tokens field."),
        )

        # Non-field errors
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Non-field specific errors."),
        )

    # Define the 'errors' field containing the validation error details
    errors = LLMUpdateErrorsDetailSerializer(
        help_text=_("Object containing validation errors."),
        read_only=True,
    )


# Permission denied error response serializer
class LLMPermissionDeniedResponseSerializer(GenericResponseSerializer):
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
        default=_("You do not have permission to update this LLM configuration."),
        read_only=True,
        help_text=_("Error message explaining the permission denial."),
    )


# LLM not found error response serializer
class LLMNotFoundResponseSerializer(GenericResponseSerializer):
    """LLM not found error response serializer.

    This serializer defines the structure of the 404 Not Found error response
    when the specified LLM cannot be found.

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
