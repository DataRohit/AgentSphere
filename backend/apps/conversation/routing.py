"""WebSocket URL routing configuration for the conversation app.

This module contains the WebSocket URL patterns for the conversation app.
"""

# Third-party imports
from django.urls import path


# Define the WebSocket URL patterns as a function to avoid circular imports
def get_conversation_websocket_urlpatterns():
    """Get the WebSocket URL patterns for the conversation app.

    This function is used to avoid circular imports by deferring the import
    of the SessionConsumer until the function is called.

    Returns:
        list: The WebSocket URL patterns for the conversation app.
    """

    # Import the SessionConsumer here to avoid circular imports
    from apps.conversation.consumers import SessionConsumer

    # Return the WebSocket URL patterns
    return [
        # Session WebSocket endpoint using the SessionConsumer class
        path("ws/conversation/session/<str:session_id>/", SessionConsumer.as_asgi()),
    ]
