# Third-party imports
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


# Class for users app configuration
class UsersConfig(AppConfig):
    """
    Configuration class for the users app.

    Extends Django's AppConfig to provide
    custom configuration for the users app.

    Attributes:
        name (str): The name of the app
        verbose_name (str): The verbose name of the app
    """

    # Attributes
    name = "apps.users"
    verbose_name = _("Users")
