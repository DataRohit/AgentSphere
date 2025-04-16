"""WebSocket URL routing configuration for AgentSphere project.

This module contains the WebSocket URL patterns for the AgentSphere project.
"""

# Third-party imports
from django.urls import path

# Local application imports
from config.websocket import websocket_application

# WebSocket URL patterns
websocket_urlpatterns = [
    # Default WebSocket endpoint
    path("ws/", websocket_application),
]
