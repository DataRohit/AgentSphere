# Standard library imports
from django.db import models
from django.utils.translation import gettext_lazy as _


# LLM API Type choices
class ApiType(models.TextChoices):
    """Enum for LLM API types.

    Defines the supported LLM API providers.

    Attributes:
        GOOGLE (str): Google Gemini API type.
    """

    # Google Gemini API type
    GOOGLE = "google", _("Google")
