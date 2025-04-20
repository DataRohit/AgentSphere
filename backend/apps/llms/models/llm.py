# Standard library imports
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

# Local application imports
from apps.common.models.timestamped import TimeStampedModel
from apps.common.utils.vault import delete_api_key, get_api_key, store_api_key
from apps.llms.models.choices import ApiType, GoogleGeminiModel
from apps.organization.models import Organization

# Get the User model
User = get_user_model()


# LLM model
class LLM(TimeStampedModel):
    """Model for LLM configurations in the system.

    This model stores the configuration details for language models including
    API type, model name, API key, and token limits.

    Attributes:
        api_type (CharField): The API provider type (Ollama or Gemini).
        model (CharField): The specific model name.
        api_key (CharField): Temporary field for API key input (not stored).
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

    # API key for authentication - not stored in DB, temporary field for input
    api_key = models.CharField(
        verbose_name=_("API Key"),
        max_length=255,
        blank=True,
        help_text=_("API key for authentication (stored securely in Vault)"),
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
        db_table = "llms_llm"

    # String representation of the LLM configuration
    def __str__(self) -> str:
        """Return a string representation of the LLM configuration.

        Returns:
            str: A string representing the LLM configuration.
        """

        # Return a formatted string with API type and model
        return f"{self.get_api_type_display()} - {self.model}"

    # Save method to handle API key storage in Vault
    def save(self, *args, **kwargs):
        """Override the save method to handle API key storage in Vault.

        Stores the API key in Vault if it's provided, then removes it from the model
        before saving to the database.
        """

        # Save the API key to Vault if provided
        is_new = self.pk is None

        # Call the parent save method first if it's a new instance to get an ID
        if is_new:
            # Set api_key to empty temporarily for first save
            temp_api_key = self.api_key
            self.api_key = ""

            # Save the model
            super().save(*args, **kwargs)

            # Restore api_key for Vault storage
            self.api_key = temp_api_key

        # Store API key in Vault if it's provided
        if self.api_key:
            # Store the API key in Vault
            store_api_key("llm", str(self.pk), self.api_key)

            # Clear the API key field before saving to the database
            self.api_key = ""

        # Call the parent save method for updates or after clearing the API key
        if not is_new:
            super().save(*args, **kwargs)

    # Get the API key from Vault
    def get_api_key(self) -> str:
        """Retrieve the API key from Vault.

        Returns:
            str: The API key if found, empty string otherwise.
        """

        # Return the API key if found, empty string otherwise
        if not self.pk:
            return ""

        # Return the API key if found, empty string otherwise
        return get_api_key("llm", str(self.pk)) or ""

    # Delete the API key from Vault
    def delete(self, *args, **kwargs) -> None:
        """Override the delete method to remove API key from Vault.

        Deletes the API key from Vault when the model instance is deleted.
        """

        # Delete the API key from Vault
        if self.pk:
            delete_api_key("llm", str(self.pk))

        # Call the parent delete method
        super().delete(*args, **kwargs)

    # Clean method to validate model selection based on API type
    def clean(self) -> None:
        """Validate model selection based on API type.

        Ensures that the selected model is compatible with the selected API type.
        """

        # Validate model selection for Google Gemini
        if self.api_type == ApiType.GOOGLE:
            # Check if the model is in the Google Gemini model choices
            if self.model not in [choice[0] for choice in GoogleGeminiModel.choices]:
                # Raise a validation error
                raise ValidationError(
                    {
                        "model": _(
                            "Invalid model for Google Gemini API. Choose from: {}",
                        ).format(
                            ", ".join([choice[0] for choice in GoogleGeminiModel.choices]),
                        ),
                    },
                )

            # Check if API key is provided for new Google Gemini instances or is available in Vault
            if not self.pk and not self.api_key:
                # Raise a validation error if API key is not provided for new instances
                raise ValidationError(
                    {"api_key": _("API key is required for Google Gemini API.")},
                )

            if self.pk and not self.api_key and not self.get_api_key():
                # Raise a validation error if API key is not available for existing instances
                raise ValidationError(
                    {"api_key": _("API key is required for Google Gemini API.")},
                )
