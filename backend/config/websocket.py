# Standard library imports
import json
from typing import Any

# Third-party imports
from channels.generic.websocket import AsyncWebsocketConsumer


# WebSocket consumer
class WebSocketConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for handling WebSocket connections.

    This consumer handles basic WebSocket connections and implements
    a simple ping/pong mechanism for testing connectivity.
    """

    # Connect method
    async def connect(self) -> None:
        """Handle WebSocket connection.

        This method is called when a WebSocket connection is established.
        """

        # Accept the WebSocket connection
        await self.accept()

    # Disconnect method
    async def disconnect(self, close_code: int) -> None:
        """Handle WebSocket disconnection.

        This method is called when a WebSocket connection is closed.

        Args:
            close_code (int): The close code for the connection.
        """

    # Receive method
    async def receive(self, text_data: str | None = None, bytes_data: bytes | None = None) -> None:
        """Handle incoming WebSocket messages.

        This method is called when a WebSocket message is received.

        Args:
            text_data (str | None): The text data received.
            bytes_data (bytes | None): The binary data received.
        """

        # If text data is received
        if text_data:
            try:
                # Parse the text data as JSON
                text_data_json: dict[str, Any] = json.loads(text_data)

                # Get the message
                message: str = text_data_json.get("message", "")

                # Handle ping message
                if message == "ping":
                    # Send a pong message
                    await self.send(text_data=json.dumps({"message": "pong"}))

            # If the text data is not valid JSON
            except json.JSONDecodeError:
                # Handle plain text messages
                if text_data == "ping":
                    # Send a pong message
                    await self.send(text_data="pong!")


# For backward compatibility with the old websocket_application function
async def websocket_application(scope: dict[str, Any], receive: Any, send: Any) -> None:
    """Legacy WebSocket application function.

    This function is maintained for backward compatibility.

    Args:
        scope (dict[str, Any]): The connection scope.
        receive (Any): The receive channel.
        send (Any): The send channel.
    """

    # Create a WebSocketConsumer instance
    consumer = WebSocketConsumer()

    # Set the scope, receive, and send channels
    consumer.scope = scope
    consumer.receive = receive
    consumer.send = send

    # Call the dispatch method
    await consumer(scope, receive, send)
