# Standard library imports
import asyncio
import contextlib
from typing import Any

# Third-party imports
from channels.generic.websocket import AsyncJsonWebsocketConsumer


# WebSocket consumer
class WebSocketConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for handling JSON WebSocket connections.

    This consumer handles JSON WebSocket connections and implements
    a simple ping/pong mechanism for testing connectivity.
    It also includes a heartbeat mechanism to keep connections alive.
    """

    # Class variables
    heartbeat_interval = 30

    # Connect method
    async def connect(self) -> None:
        """Handle WebSocket connection.

        This method is called when a WebSocket connection is established.
        """

        # Accept the WebSocket connection
        await self.accept()

        # Start heartbeat task
        self.heartbeat_task = asyncio.create_task(self.heartbeat())

    # Disconnect method
    async def disconnect(self, close_code: int) -> None:
        """Handle WebSocket disconnection.

        This method is called when a WebSocket connection is closed.

        Args:
            close_code (int): The close code for the connection.
        """

        # If the heartbeat task exists
        if hasattr(self, "heartbeat_task"):
            # Cancel the heartbeat task
            self.heartbeat_task.cancel()

            # Try to await the heartbeat task
            with contextlib.suppress(asyncio.CancelledError):
                # Await the heartbeat task
                await self.heartbeat_task

    # Receive JSON method
    async def receive_json(self, content: dict[str, Any], **kwargs) -> None:
        """Handle incoming JSON WebSocket messages.

        This method is called when a JSON WebSocket message is received.
        The content is already decoded from JSON.

        Args:
            content (dict[str, Any]): The decoded JSON data received.
        """

        # Get the message type/content from the decoded JSON
        message: str = content.get("message", "")

        # Handle ping message
        if message == "ping":
            # Send a pong message using send_json
            await self.send_json({"message": "pong"})

    # Heartbeat method to keep the connection alive
    async def heartbeat(self) -> None:
        """Send periodic heartbeat messages to keep the connection alive.

        This method runs in the background and sends a heartbeat message
        every heartbeat_interval seconds.
        """

        # While True
        while True:
            # Wait for the specified interval
            await asyncio.sleep(self.heartbeat_interval)

            # Send a heartbeat message using send_json
            await self.send_json({"type": "heartbeat"})
