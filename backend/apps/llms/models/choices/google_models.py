# Standard library imports
from django.db import models
from django.utils.translation import gettext_lazy as _


# Google Gemini model choices
class GoogleGeminiModel(models.TextChoices):
    """Enum for Google Gemini model types.

    Defines the supported Google Gemini models.

    Attributes:
        PRO_PREVIEW (str): Gemini 2.5 Pro Preview model.
        FLASH_PREVIEW (str): Gemini 2.5 Flash Preview model.
        FLASH (str): Gemini 2.0 Flash model.
        FLASH_LITE (str): Gemini 2.0 Flash Lite model.
        THINKING (str): Gemini 2.0 Flash Thinking Experimental model.
    """

    # Gemini 2.5 Pro Preview
    PRO_PREVIEW = "gemini-2.5-pro-preview-03-25", _("Gemini 2.5 Pro Preview")

    # Gemini 2.5 Flash Preview
    FLASH_PREVIEW = "gemini-2.5-flash-preview-04-17", _("Gemini 2.5 Flash Preview")

    # Gemini 2.0 Flash
    FLASH = "gemini-2.0-flash-001", _("Gemini 2.0 Flash")

    # Gemini 2.0 Flash Lite
    FLASH_LITE = "gemini-2.0-flash-lite-001", _("Gemini 2.0 Flash Lite")

    # Gemini 2.0 Flash Thinking
    THINKING = "gemini-2.0-flash-thinking-exp-01-21", _("Gemini 2.0 Flash Thinking")
