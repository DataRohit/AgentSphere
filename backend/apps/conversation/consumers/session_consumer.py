# Standard library imports
import uuid
from contextlib import suppress
from typing import Any

# Third-party imports
from asgiref.sync import sync_to_async
from autogen_agentchat.messages import TextMessage
from autogen_core import FunctionCall
from autogen_core.models import FunctionExecutionResult
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

# Local application imports
from apps.chats.models import Message
from apps.conversation.autogen.agents import process_with_agents
from apps.conversation.autogen.database import (
    deactivate_session as deactivate_session_db,
)
from apps.conversation.autogen.database import (
    get_agent,
    get_agent_id_for_single_chat,
    get_agents_for_group_chat,
    get_chat_info,
    get_previous_messages,
    save_message,
)
from apps.conversation.autogen.database import (
    get_session as get_session_db,
)
from apps.conversation.autogen.messages import (
    handle_ping_message,
    send_connection_confirmation,
    send_direct_response,
    send_error_message,
    send_function_call,
    send_function_execution_result,
)
from apps.conversation.models import Session
from apps.conversation.tasks.generate_chat_summary import generate_chat_summary


# Session WebSocket consumer
class SessionConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for handling session connections.

    This consumer handles WebSocket connections for chat sessions.
    It implements a simple ping/pong mechanism for testing connectivity.

    When a user sends a message, it is saved to the database but not echoed back to the client.
    Only the agent's response is sent back to the client to prevent duplicate messages.

    Attributes:
        session (Session): The session associated with this connection.
    """

    # Initialize the consumer
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the consumer.

        Args:
            *args (Any): Variable length argument list.
            **kwargs (Any): Arbitrary keyword arguments.
        """

        # Call the parent class constructor
        super().__init__(*args, **kwargs)

        # Initialize the session
        self.session = None

    # Setup single chat agents
    async def _setup_single_chat(self) -> str | None:
        """Set up single chat agents.

        Returns:
            str | None: Error message if setup fails, None if successful
        """

        # Get the agent id for the single chat
        self.agent_id = await get_agent_id_for_single_chat(self.chat.id)

        # If the agent id is not found
        if not self.agent_id:
            # Return error message
            return "Error: Agent ID not found for single chat."

        try:
            # Get the agent
            agent = await get_agent(self.agent_id)

            # If agent is available
            if agent:
                # Set the agents list
                self.agents = [agent]

                # Return none
                return None

        except (ValueError, TypeError, AttributeError) as e:
            # Return error message
            return f"Error retrieving agent: {e!s}"

        # Return error message
        return "Error: Could not retrieve agent for single chat."

    # Setup group chat agents
    async def _setup_group_chat(self) -> str | None:
        """Set up group chat agents.

        Returns:
            str | None: Error message if setup fails, None if successful
        """

        try:
            # Get the agents for the group chat
            self.agents = await get_agents_for_group_chat(self.chat.id)

            # If no agents were retrieved
            if not self.agents:
                # Return error message
                return "Error: No agents found for group chat."

        except (ValueError, TypeError, AttributeError) as e:
            # Return error message
            return f"Error retrieving agents for group chat: {e!s}"

        # Return non
        return None

    # Setup chat & agents for chat
    async def _setup_chat_and_agents(self) -> tuple[bool, str | None]:
        """Set up chat type and agents.

        Returns:
            tuple[bool, str | None]: (Success status, Error message if failed)
        """

        # Get the chat type & chat
        chat_info = await get_chat_info(self.session_id)

        # If not chat info found
        if not chat_info:
            # Return error message
            return False, "Error: Session exists but chat information is missing."

        # Get the chat type
        self.chat_type = chat_info["type"]

        # Get the chat object
        self.chat = chat_info["chat"]

        # If chat type is single
        if self.chat_type == "single":
            # Setup single chat
            error = await self._setup_single_chat()

        # If chat type is group
        elif self.chat_type == "group":
            # Setup group chat
            error = await self._setup_group_chat()

        # If chat type is not supported
        else:
            # Return error message
            error = f"Unsupported chat type: {self.chat_type}"

        # Return success status and error message
        return error is None, error

    # Connect method
    async def connect(self) -> None:
        """Handle WebSocket connection.

        This method is called when a WebSocket connection is established.
        It validates the session ID from the URL and accepts the connection
        if the session exists and is active and the user is authenticated.
        """

        # Get the user from the scope
        self.user = self.scope.get("user", AnonymousUser())

        # Get the session ID from the URL route
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]

        try:
            # Get the session from the database
            self.session = await get_session_db(uuid.UUID(self.session_id))

            # If the session doesn't exist or is not active
            if not self.session or not self.session.is_active:
                # Reject the connection
                await self.close(code=4004)

                # Return
                return

            # Accept the WebSocket connection
            await self.accept()

            # Add the connection to the session group
            await self.channel_layer.group_add(
                f"session_{self.session_id}",
                self.channel_name,
            )

            # Set up chat and agents
            success, error = await self._setup_chat_and_agents()

            # If setup failed
            if not success:
                # Send error message
                await send_error_message(self, error)

                # Reject the connection
                await self.close(code=1011)

                # Return
                return

            # If no error
            with suppress(Exception):
                # Send connection confirmation
                await send_connection_confirmation(self)

        # If the session ID is invalid
        except (ValueError, Session.DoesNotExist):
            # Reject the connection if the session ID is invalid
            await self.close()

    # Disconnect method
    async def disconnect(self, close_code: int) -> None:
        """Handle WebSocket disconnection.

        This method is called when a WebSocket connection is closed.
        It deactivates the session when the client disconnects and triggers
        a task to generate a summary of the conversation.

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
                await deactivate_session_db(self.session_id)

                # Trigger the task to generate a summary of the conversation
                await self.generate_chat_summary(self.session_id)

    # Chat message handler
    async def chat_message(self, event: dict[str, Any]) -> None:
        """Handle chat messages from the channel layer.

        This method is called when a message is received from the channel layer.
        It sends the message to the client.

        Args:
            event (dict[str, Any]): The event containing the message.
        """

        with suppress(Exception):
            # Send the message to the client
            await self.send_json(event["message"])

    # Receive JSON method
    async def receive_json(self, request: dict[str, Any], **kwargs) -> None:  # noqa: C901
        """Handle incoming JSON WebSocket messages.

        This method is called when a JSON WebSocket message is received.
        The request is already decoded from JSON.

        User messages are saved to the database but not echoed back to the client.
        Only agent responses are sent back to the client to prevent duplicate messages.

        Args:
            request (dict[str, Any]): The decoded JSON data received.
        """

        try:
            # If the request is not a dictionary or doesn't have the required fields
            if not isinstance(request, dict) or "content" not in request or "source" not in request:
                # Send an error message
                await send_error_message(
                    self,
                    "Invalid message format. Expected 'content' and 'source' fields.",
                )

                # Return
                return

            # Decode the request into a TextMessage
            message = TextMessage.model_validate(request)

            # Handle ping message
            if message.content == "ping" and message.source == "user":
                # Send pong message
                await handle_ping_message(self)

                # Return
                return

            # If message source is user
            if message.source == "user":
                try:
                    # Save the user message to the database
                    await save_message(
                        session=self.session,
                        content=message.content,
                        sender=Message.SenderType.USER,
                        user_id=self.user.id if self.user else None,
                    )

                    # Get previous messages
                    previous_messages = await get_previous_messages(self.session)

                    # Define a callback to handle each message as it arrives
                    async def message_callback(
                        agent_id: str,
                        source: str,
                        response_content: str | list[FunctionCall] | list[FunctionExecutionResult],
                    ) -> None:
                        """Handle each message as it arrives.

                        Args:
                            agent_id (str): The ID of the agent that sent the message.
                            source (str): The source of the message.
                            response_content (str | list[FunctionCall] | list[FunctionExecutionResult]): The content of the message.
                        """  # noqa: E501

                        # Check if this is a function call or execution result message
                        is_function_message = not isinstance(response_content, str)

                        # Only save non-function messages to the database
                        if not is_function_message:
                            # Send direct response to client immediately
                            await send_direct_response(self, source, str(response_content))

                            # Save the message to the database
                            await save_message(
                                self.session,
                                content=response_content,
                                sender=Message.SenderType.AGENT,
                                agent_id=agent_id,
                            )

                        else:
                            # Traverse over the response content
                            for item in response_content:
                                # If the item is a function call
                                if isinstance(item, FunctionCall):
                                    # Send function call to client immediately
                                    await send_function_call(self, item)

                                # If the item is a function execution result
                                elif isinstance(item, FunctionExecutionResult):
                                    # Send function execution result to client immediately
                                    await send_function_execution_result(self, item)

                    # Process the user message with agents, passing the callback
                    agent_response = await process_with_agents(
                        self.chat_type,
                        self.session,
                        message.content,
                        self.agents,
                        {"previous_messages": previous_messages, "message_callback": message_callback},
                    )

                    # If no agent responses were received
                    if not agent_response and self.agents:
                        # Create a default response
                        default_response = (
                            self.agents[0].id,
                            "agent",
                            "I'm sorry, I couldn't process your request at this time.",
                        )

                        # Send the default response
                        await message_callback(*default_response)

                # If an error occurs
                except (ValueError, TypeError, AttributeError) as e:
                    # Send error message
                    await send_error_message(self, f"Error processing message: {e!s}")

        # If an error occurs
        except (ValueError, TypeError, AttributeError) as e:
            # Send error message
            await send_error_message(self, f"Error processing message: {e!s}")

    # Method to trigger the chat summary generation task
    @sync_to_async
    def generate_chat_summary(self, session_id: uuid.UUID) -> None:
        """Trigger the task to generate a summary of the conversation.

        This method triggers a Celery task to generate a summary of the conversation
        associated with the specified session.

        Args:
            session_id (uuid.UUID): The ID of the session.
        """

        # Trigger the task
        generate_chat_summary.delay(str(session_id))
