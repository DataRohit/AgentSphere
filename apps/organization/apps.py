# Third-party imports
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


# Class for organization app configuration
class OrganizationConfig(AppConfig):
    """
    Configuration class for the organization app.

    Extends Django's AppConfig to provide
    custom configuration for the organization app.

    Attributes:
        name (str): The name of the app
        verbose_name (str): The verbose name of the app
    """

    # Attributes
    name = "apps.organization"
    verbose_name = _("Organization")
