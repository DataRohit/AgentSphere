# Third-party imports
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


# Class for conversation app configuration
class ConversationConfig(AppConfig):
    """
    Configuration class for the conversation app.

    Extends Django's AppConfig to provide
    custom configuration for the conversation app.

    Attributes:
        name (str): The name of the app
        verbose_name (str): The verbose name of the app
    """

    # Attributes
    name = "apps.conversation"
    verbose_name = _("Conversation")
