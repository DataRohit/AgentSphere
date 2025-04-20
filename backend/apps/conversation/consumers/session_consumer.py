# Standard library imports
import asyncio
import contextlib
import uuid
from typing import Any

# Third-party imports
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

# Local application imports
from apps.conversation.models import Session


# Session WebSocket consumer
class SessionConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for handling session connections.

    This consumer handles WebSocket connections for chat sessions.
    It implements a simple ping/pong mechanism for testing connectivity
    and includes a heartbeat mechanism to keep connections alive.

    Attributes:
        heartbeat_interval (int): The interval in seconds for sending heartbeat messages.
        session (Session): The session associated with this connection.
    """

    # Class variables
    heartbeat_interval = 30

    # Connect method
    async def connect(self) -> None:
        """Handle WebSocket connection.

        This method is called when a WebSocket connection is established.
        It validates the session ID from the URL and accepts the connection
        if the session exists and is active.
        """

        # Get the session ID from the URL route
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]

        try:
            # Convert the session ID to a UUID
            session_uuid = uuid.UUID(self.session_id)

            # Get the session from the database
            self.session = await self.get_session(session_uuid)

            # If the session exists and is active
            if self.session and self.session.is_active:
                # Accept the WebSocket connection
                await self.accept()

                # Add the connection to the session group
                await self.channel_layer.group_add(
                    f"session_{self.session_id}",
                    self.channel_name,
                )

                # Start heartbeat task
                self.heartbeat_task = asyncio.create_task(self.heartbeat())

            else:
                # Reject the connection if the session doesn't exist or is not active
                await self.close()

        # If the session ID is invalid
        except (ValueError, Session.DoesNotExist):
            # Reject the connection if the session ID is invalid
            await self.close()

    # Disconnect method
    async def disconnect(self, close_code: int) -> None:
        """Handle WebSocket disconnection.

        This method is called when a WebSocket connection is closed.
        It deactivates the session when the client disconnects.

        Args:
            close_code (int): The close code for the connection.
        """

        # If the session ID is set
        if hasattr(self, "session_id"):
            # Remove the connection from the session group
            await self.channel_layer.group_discard(
                f"session_{self.session_id}",
                self.channel_name,
            )

            # If the session exists
            if hasattr(self, "session"):
                # Deactivate the session
                await self.deactivate_session(self.session.id)

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

    # Database method to get a session
    @database_sync_to_async
    def get_session(self, session_id: uuid.UUID) -> Session:
        """Get a session from the database.

        Args:
            session_id (uuid.UUID): The ID of the session to get.

        Returns:
            Session: The session with the specified ID.

        Raises:
            Session.DoesNotExist: If the session doesn't exist.
        """

        # Get and return the session
        return Session.objects.get(id=session_id)

    # Database method to deactivate a session
    @database_sync_to_async
    def deactivate_session(self, session_id: uuid.UUID) -> None:
        """Deactivate a session in the database.

        This method sets the is_active field to False for the specified session.
        The updated_at field will be automatically updated since the Session model
        inherits from TimeStampedModel.

        Args:
            session_id (uuid.UUID): The ID of the session to deactivate.
        """

        try:
            # Get the session
            session = Session.objects.get(id=session_id)

            # Set is_active to False
            session.is_active = False

            # Save the session
            session.save()

        # If the session does not exist
        except Session.DoesNotExist:
            # Pass
            pass
