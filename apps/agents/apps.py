# Third-party imports
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


# Class for agents app configuration
class AgentsConfig(AppConfig):
    """
    Configuration class for the agents app.

    Extends Django's AppConfig to provide
    custom configuration for the agents app.

    Attributes:
        name (str): The name of the app
        verbose_name (str): The verbose name of the app
    """

    # Attributes
    name = "apps.agents"
    verbose_name = _("Agents")
