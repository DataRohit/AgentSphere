"""ASGI configuration for AgentSphere project.

This module contains the ASGI application used by Django's development server
and any production ASGI deployments.
"""

# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

# Set the base directory for the project
BASE_DIR: Path = Path(__file__).resolve(strict=True).parent.parent

# Add the apps directory to the Python path
sys.path.append(str(BASE_DIR / "apps"))

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Import websocket routing configuration
from config.routing import websocket_urlpatterns  # noqa: E402

# Configure the ASGI application with protocol routing
application = ProtocolTypeRouter(
    {
        # Django's ASGI application for HTTP requests
        "http": get_asgi_application(),
        # WebSocket handler with authentication and origin validation
        "websocket": AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns))),
    },
)
