# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer
from apps.llms.models import LLM, ApiType, GoogleGeminiModel
from apps.llms.serializers.llm import LLMResponseSchema
from apps.organization.models import Organization


# LLM creation serializer
class LLMCreateSerializer(serializers.ModelSerializer):
    """LLM creation serializer.

    This serializer handles the creation of new LLM configurations. It validates that
    the user is a member of the specified organization and ensures the provided model
    is valid for the selected API type.

    Attributes:
        organization_id (UUIDField): The ID of the organization to associate the LLM with.
        api_type (CharField): The API provider type (Gemini).
        model (CharField): The specific model name.
        api_key (CharField): API key for authentication (required for Gemini).
        max_tokens (PositiveIntegerField): Maximum tokens for generation.

    Meta:
        model (LLM): The LLM model.
        fields (list): The fields to include in the serializer.
        extra_kwargs (dict): Additional field configurations.

    Raises:
        serializers.ValidationError: If user is not a member of the organization.
        serializers.ValidationError: If the model is not valid for the API type.
        serializers.ValidationError: If API key is missing for Gemini.

    Returns:
        LLM: The newly created LLM instance.
    """

    # Organization ID field
    organization_id = serializers.UUIDField(
        required=True,
        help_text=_("ID of the organization to associate the LLM with."),
    )

    # Meta class for LLMCreateSerializer configuration
    class Meta:
        """Meta class for LLMCreateSerializer configuration.

        Attributes:
            model (LLM): The model class.
            fields (list): The fields to include in the serializer.
            extra_kwargs (dict): Additional field configurations.
        """

        # Model to use for the serializer
        model = LLM

        # Fields to include in the serializer
        fields = [
            "organization_id",
            "api_type",
            "model",
            "api_key",
            "max_tokens",
        ]

        # Extra kwargs
        extra_kwargs = {
            "api_type": {"required": True},
            "model": {"required": True},
            "api_key": {"required": False, "write_only": True},
            "max_tokens": {"required": False},
        }

    # Validate the serializer data
    def validate(self, attrs: dict) -> dict:
        """Validate the serializer data.

        This method validates that:
        1. The user is a member of the specified organization.
        2. The model is valid for the selected API type.
        3. API key is provided for Gemini API type.
        4. The user has not exceeded the maximum number of LLM configurations they can create.

        Args:
            attrs (dict): The attributes to validate.

        Returns:
            dict: The validated attributes.

        Raises:
            serializers.ValidationError: If validation fails.
        """

        # Get the user from the context
        user = self.context["request"].user

        # Get the organization ID
        organization_id = attrs.get("organization_id")

        # Get the API type and model
        api_type = attrs.get("api_type")
        model = attrs.get("model")

        # Get the API key
        api_key = attrs.get("api_key", "")

        try:
            # Try to get the organization
            organization = Organization.objects.get(id=organization_id)

            # Check if the user is a member of the organization
            if user not in organization.members.all() and user != organization.owner:
                # Raise a validation error
                raise serializers.ValidationError(
                    {
                        "organization_id": [
                            _("You are not a member of this organization."),
                        ],
                    },
                ) from None

            # Validate model selection for Gemini
            if api_type == ApiType.GOOGLE:
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
                    ) from None

                # Check if API key is provided for Gemini
                if not api_key:
                    # Raise a validation error
                    raise serializers.ValidationError(
                        {"api_key": [_("API key is required for Gemini API.")]},
                    ) from None

            # Store the organization in attrs for later use
            attrs["organization"] = organization

            # Store the user in attrs for later use
            attrs["user"] = user

            # Remove the organization_id from attrs as it's not a field in the LLM model
            del attrs["organization_id"]

        except Organization.DoesNotExist:
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "organization_id": [
                        _("Organization not found."),
                    ],
                },
            ) from None

        # Return the validated attributes
        return attrs

    # Create a new LLM configuration
    def create(self, validated_data):
        """Create a new LLM configuration.

        This method creates a new LLM configuration with the organization and user set from validated data.
        The API key handling is done by the model's save method.

        Args:
            validated_data (dict): The validated data.

        Returns:
            LLM: The newly created LLM configuration.
        """

        # Get the organization from validated data
        organization = validated_data.pop("organization")

        # Get the user from validated data
        user = validated_data.pop("user")

        # Return the created LLM
        return LLM.objects.create(
            organization=organization,
            user=user,
            **validated_data,
        )


# LLM creation success response serializer
class LLMCreateSuccessResponseSerializer(GenericResponseSerializer):
    """LLM creation success response serializer.

    This serializer defines the structure of the LLM creation success response.
    It includes a status code and an LLM object.

    Attributes:
        status_code (int): The status code of the response.
        llm (LLMResponseSchema): The newly created LLM with detailed organization and user information.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_201_CREATED,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # LLM data
    llm = LLMResponseSchema(
        help_text=_(
            "The newly created LLM with detailed organization and user information.",
        ),
        read_only=True,
    )


# LLM creation error response serializer
class LLMCreateErrorResponseSerializer(GenericResponseSerializer):
    """LLM creation error response serializer (for schema).

    This serializer defines the structure of the wrapped validation error response
    as it would be formatted for documentation purposes.

    Attributes:
        status_code (int): The status code of the response.
        errors (LLMCreateErrorsDetailSerializer): The errors detail serializer.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Nested serializer defining the structure of the actual errors
    class LLMCreateErrorsDetailSerializer(serializers.Serializer):
        """LLM Creation Errors detail serializer.

        Attributes:
            organization_id (list): Errors related to the organization ID field.
            api_type (list): Errors related to the API type field.
            model (list): Errors related to the model field.
            api_key (list): Errors related to the API key field.
            max_tokens (list): Errors related to the max tokens field.
            non_field_errors (list): Non-field specific errors.
        """

        # Organization ID field
        organization_id = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the organization ID field."),
        )

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
    errors = LLMCreateErrorsDetailSerializer(
        help_text=_("Object containing validation errors."),
        read_only=True,
    )


# LLM authentication error response serializer
class LLMAuthErrorResponseSerializer(GenericResponseSerializer):
    """Authentication error response serializer.

    This serializer defines the structure of the authentication error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response (401 Unauthorized).
        error (str): An error message explaining the authentication failure.
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
        help_text=_("Error message explaining the authentication failure."),
    )
