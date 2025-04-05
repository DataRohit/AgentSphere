"""ASGI configuration for AgentSphere project.

This module contains the ASGI application used by Django's development server
and any production ASGI deployments.
"""

# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
from django.core.asgi import get_asgi_application
from django.core.handlers.asgi import ASGIHandler

# Project imports
from config.websocket import websocket_application

# Set the base directory for the project
BASE_DIR: Path = Path(__file__).resolve(strict=True).parent.parent

# Add the apps directory to the Python path
sys.path.append(str(BASE_DIR / "apps"))

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Get the ASGI application
django_application: ASGIHandler = get_asgi_application()


# This is the main function that will be used to handle the ASGI connection
async def application(scope, receive, send):
    # If the scope is a HTTP request
    if scope["type"] == "http":
        # Call the Django application
        await django_application(scope, receive, send)

    # If the scope is a websocket connection
    elif scope["type"] == "websocket":
        # Call the websocket application
        await websocket_application(scope, receive, send)

    # If the scope is not a HTTP request or websocket connection
    else:
        # Raise an error
        msg = f"Unknown scope type {scope['type']}"
        raise NotImplementedError(msg)
