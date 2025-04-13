# Third-party imports
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


# Class for common app configuration
class CommonConfig(AppConfig):
    """
    Configuration class for the common app.

    Extends Django's AppConfig to provide
    custom configuration for the common app.

    Attributes:
        name (str): The name of the app
        verbose_name (str): The verbose name of the app
    """

    # Attributes
    name = "apps.common"
    verbose_name = _("Common")
