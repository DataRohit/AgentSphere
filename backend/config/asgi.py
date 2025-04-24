"""ASGI configuration for AgentSphere project.

This module contains the ASGI application used by Django's development server
and any production ASGI deployments.
"""

# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

# Local application imports
from config.middleware import JWTAuthMiddlewareStack

# Set the base directory for the project
BASE_DIR: Path = Path(__file__).resolve(strict=True).parent.parent

# Add the apps directory to the Python path
sys.path.append(str(BASE_DIR / "apps"))

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Get the Django ASGI application first
django_asgi_app = get_asgi_application()


# Define a function to get the WebSocket application
def get_websocket_application() -> URLRouter:
    """Get the WebSocket application.

    This function is used to defer the import of the websocket_urlpatterns
    until the function is called, after Django is fully set up.

    Returns:
        URLRouter: The WebSocket URL router.
    """

    # Import websocket routing configuration after Django is set up
    from config.routing import websocket_urlpatterns

    # Return the WebSocket URL router
    return URLRouter(websocket_urlpatterns)


# Configure the ASGI application with protocol routing
application = ProtocolTypeRouter(
    {
        # Django's ASGI application for HTTP requests
        "http": django_asgi_app,
        # WebSocket handler with JWT authentication and origin validation
        "websocket": AllowedHostsOriginValidator(JWTAuthMiddlewareStack(get_websocket_application())),
    },
)
