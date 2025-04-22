# Third party imports
from autogen_core.models import ModelFamily

# Standard library imports
from django.db import models
from django.utils.translation import gettext_lazy as _


# Google Gemini model choices
class GoogleGeminiModel(models.TextChoices):
    """Enum for Google Gemini model types.

    Defines the supported Google Gemini models.

    Attributes:
        PRO_25 (str): Gemini 2.5 Pro model.
        FLASH_20 (str): Gemini 2.0 Flash model.
        PRO_15 (str): Gemini 1.5 Pro model.
        FLASH_15 (str): Gemini 1.5 Flash model.
    """

    # Gemini 2.5 Pro
    PRO_2_5 = ModelFamily.GEMINI_2_5_PRO, _("Gemini 2.5 Pro")

    # Gemini 2.0 Flash
    FLASH_2_0 = ModelFamily.GEMINI_2_0_FLASH, _("Gemini 2.0 Flash")

    # Gemini 1.5 Pro
    PRO_1_5 = ModelFamily.GEMINI_1_5_PRO, _("Gemini 1.5 Pro")

    # Gemini 1.5 Flash
    FLASH_1_5 = ModelFamily.GEMINI_1_5_FLASH, _("Gemini 1.5 Flash")
