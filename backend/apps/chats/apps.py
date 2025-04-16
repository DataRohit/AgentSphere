# Third-party imports
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


# Class for chats app configuration
class ChatsConfig(AppConfig):
    """
    Configuration class for the chats app.

    Extends Django's AppConfig to provide
    custom configuration for the chats app.

    Attributes:
        name (str): The name of the app
        verbose_name (str): The verbose name of the app
    """

    # Attributes
    name = "apps.chats"
    verbose_name = _("Chats")
