# Standard library imports
from django.db import models
from django.utils.translation import gettext_lazy as _


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
