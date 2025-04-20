"""WebSocket URL routing configuration for AgentSphere project.

This module contains the WebSocket URL patterns for the AgentSphere project.
"""

# Local application imports
from apps.conversation.routing import get_conversation_websocket_urlpatterns

# Third-party imports
from django.urls import path

# Local application imports
from config.websocket import WebSocketConsumer

# WebSocket URL patterns
websocket_urlpatterns = [
    # Default WebSocket endpoint using the WebSocketConsumer class
    path("ws/", WebSocketConsumer.as_asgi()),
]

# Add conversation app WebSocket routes
websocket_urlpatterns.extend(get_conversation_websocket_urlpatterns())
