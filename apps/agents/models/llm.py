# Standard library imports
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

# Local application imports
from apps.common.models.timestamped import TimeStampedModel
from apps.organization.models import Organization

# Get the User model
User = get_user_model()


# LLM API Type choices
class ApiType(models.TextChoices):
    """Enum for LLM API types.

    Defines the supported LLM API providers.

    Attributes:
        OLLAMA (str): Ollama API type.
        GEMINI (str): Google Gemini API type.
    """

    # Ollama API type
    OLLAMA = "ollama", _("Ollama")

    # Gemini API type
    GEMINI = "gemini", _("Gemini")


# Ollama model choices
class OllamaModel(models.TextChoices):
    """Enum for Ollama model types.

    Defines the supported Ollama models.

    Attributes:
        GRANITE (str): Granite 3.1 Dense 2B Instruct Q8_0 model.
        QWEN (str): Qwen 2.5 1.5B Instruct Q8_0 model.
        LLAMA (str): Llama 3.2 1B Instruct Q8_0 model.
        DEEPSEEK (str): DeepSeek R1 1.5B Qwen Distill Q8_0 model.
    """

    # Granite 3.1 2B
    GRANITE = "granite3.1-dense:2b-instruct-q8_0", _("Granite 3.1 2B")

    # Qwen 2.5 1.5B
    QWEN = "qwen2.5:1.5b-instruct-q8_0", _("Qwen 2.5 1.5B")

    # Llama 3.2 1B
    LLAMA = "llama3.2:1b-instruct-q8_0", _("Llama 3.2 1B")

    # DeepSeek R1 1.5B
    DEEPSEEK = "deepseek-r1:1.5b-qwen-distill-q8_0", _("DeepSeek R1 1.5B")


# Gemini model choices
class GeminiModel(models.TextChoices):
    """Enum for Gemini model types.

    Defines the supported Google Gemini models.

    Attributes:
        FLASH (str): Gemini 2.0 Flash model.
        FLASH_LITE (str): Gemini 2.0 Flash Lite model.
        THINKING (str): Gemini 2.0 Flash Thinking Experimental model.
    """

    # Gemini 2.0 Flash
    FLASH = "gemini-2.0-flash", _("Gemini 2.0 Flash")

    # Gemini 2.0 Flash Lite
    FLASH_LITE = "gemini-2.0-flash-lite", _("Gemini 2.0 Flash Lite")

    # Gemini 2.0 Flash Thinking
    THINKING = "gemini-2.0-flash-thinking-exp-01-21", _("Gemini 2.0 Flash Thinking")


# LLM model
class LLM(TimeStampedModel):
    """Model for LLM configurations in the system.

    This model stores the configuration details for language models including
    API type, model name, API key, and token limits.

    Attributes:
        api_type (CharField): The API provider type (Ollama or Gemini).
        model (CharField): The specific model name.
        api_key (CharField): API key for authentication.
        max_tokens (PositiveIntegerField): Maximum tokens for generation.
        organization (ForeignKey): The organization this configuration belongs to.
        user (ForeignKey): The user who created this configuration.

    Meta:
        verbose_name (str): Human-readable name for the model.
        verbose_name_plural (str): Human-readable plural name for the model.
        ordering (list): Default ordering for model instances.
        db_table (str): The database table name.
    """

    # API type (Ollama or Gemini)
    api_type = models.CharField(
        verbose_name=_("API Type"),
        max_length=10,
        choices=ApiType.choices,
    )

    # Model name
    model = models.CharField(
        verbose_name=_("Model"),
        max_length=100,
        help_text=_("The specific model name for the selected API type"),
    )

    # API key for authentication
    api_key = models.CharField(
        verbose_name=_("API Key"),
        max_length=255,
        blank=True,
        help_text=_("API key for authentication provided by the API provider."),
    )

    # Maximum tokens for generation
    max_tokens = models.PositiveIntegerField(
        verbose_name=_("Max Tokens"),
        default=4096,
        help_text=_("Maximum number of tokens for generation"),
    )

    # Organization the configuration belongs to
    organization = models.ForeignKey(
        Organization,
        verbose_name=_("Organization"),
        on_delete=models.CASCADE,
        related_name="llm_configs",
        null=True,
        blank=True,
    )

    # User who created the configuration
    user = models.ForeignKey(
        User,
        verbose_name=_("Created By"),
        on_delete=models.CASCADE,
        related_name="created_llm_configs",
        null=True,
        blank=True,
    )

    # Meta class for LLM model configuration
    class Meta:
        """Meta class for LLM model configuration.

        Attributes:
            verbose_name (str): Human-readable name for the model.
            verbose_name_plural (str): Human-readable plural name for the model.
            ordering (list): Default ordering for model instances.
            db_table (str): The database table name.
        """

        # Human-readable model name
        verbose_name = _("LLM")

        # Human-readable plural model name
        verbose_name_plural = _("LLMs")

        # Default ordering by API type and model
        ordering = ["api_type", "model"]

        # Specify the database table name
        db_table = "agents_llm"

    # String representation of the LLM configuration
    def __str__(self) -> str:
        """Return a string representation of the LLM configuration.

        Returns:
            str: A string representing the LLM configuration.
        """

        # Return a formatted string with API type and model
        return f"{self.get_api_type_display()} - {self.model}"

    # Clean method to validate model selection based on API type
    def clean(self):
        """Validate model selection based on API type.

        Ensures that the selected model is compatible with the selected API type.
        """

        # Import for validation
        from django.core.exceptions import ValidationError

        # Validate model selection for Ollama
        if self.api_type == ApiType.OLLAMA:
            # Check if the model is in the Ollama model choices
            if self.model not in [choice[0] for choice in OllamaModel.choices]:
                raise ValidationError(
                    {
                        "model": _(
                            "Invalid model for Ollama API. Choose from: {}",
                        ).format(
                            ", ".join([choice[0] for choice in OllamaModel.choices]),
                        ),
                    },
                )

        # Validate model selection for Gemini
        elif self.api_type == ApiType.GEMINI:
            # Check if the model is in the Gemini model choices
            if self.model not in [choice[0] for choice in GeminiModel.choices]:
                raise ValidationError(
                    {
                        "model": _(
                            "Invalid model for Gemini API. Choose from: {}",
                        ).format(
                            ", ".join([choice[0] for choice in GeminiModel.choices]),
                        ),
                    },
                )

            # Check if API key is provided for Gemini
            if not self.api_key:
                # Raise a validation error if API key is not provided
                raise ValidationError(
                    {"api_key": _("API key is required for Gemini API.")},
                )
