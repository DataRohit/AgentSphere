# Standard library imports
from contextlib import suppress

# Third party imports
from autogen_agentchat.messages import TextMessage, ToolCallExecutionEvent, ToolCallRequestEvent
from autogen_core import FunctionCall
from autogen_core.models import FunctionExecutionResult
from channels.generic.websocket import AsyncJsonWebsocketConsumer


# Handle ping message
async def handle_ping_message(consumer: AsyncJsonWebsocketConsumer) -> None:
    """Handle ping message from client.

    Args:
        consumer (AsyncJsonWebsocketConsumer): The WebSocket consumer.
    """

    with suppress(Exception):
        # Send a pong message using send_json
        await consumer.send_json(TextMessage(content="pong", source="server", metadata={"error": "false"}).model_dump())


# Send error message
async def send_error_message(consumer: AsyncJsonWebsocketConsumer, error_message: str) -> None:
    """Send an error message to the client.

    Args:
        consumer (AsyncJsonWebsocketConsumer): The WebSocket consumer.
        error_message (str): The error message to send.
    """

    with suppress(Exception):
        # Send the error message
        await consumer.send_json(
            TextMessage(
                content=error_message,
                source="server",
                metadata={"error": "true"},
            ).model_dump(),
        )


# Send connection confirmation
async def send_connection_confirmation(consumer: AsyncJsonWebsocketConsumer) -> None:
    """Send connection confirmation message to the client.

    Args:
        consumer (AsyncJsonWebsocketConsumer): The WebSocket consumer.
    """

    with suppress(Exception):
        # Send the connection confirmation
        await consumer.send_json(
            TextMessage(
                content="connected",
                source="server",
                metadata={
                    "error": "false",
                },
            ).model_dump(),
        )


# Send direct response
async def send_direct_response(
    consumer: AsyncJsonWebsocketConsumer,
    source: str,
    content: str,
) -> None:
    """Send a direct response to the client.

    Args:
        consumer (AsyncJsonWebsocketConsumer): The WebSocket consumer.
        source (str): The source of the message.
        content (str): The content of the message.
    """

    with suppress(Exception):
        # Send the message directly to the client
        await consumer.send_json(TextMessage(content=content, source=source, metadata={"error": "false"}).model_dump())


# Send function call
async def send_function_call(consumer: AsyncJsonWebsocketConsumer, function_call: FunctionCall) -> None:
    """Send a function call to the client.

    Args:
        consumer (AsyncJsonWebsocketConsumer): The WebSocket consumer.
        function_call (FunctionCall): The function call to send.
    """

    with suppress(Exception):
        # Send the function call to the client
        await consumer.send_json(
            ToolCallRequestEvent(
                content=[function_call],
                source="server",
                metadata={"error": "false"},
            ).model_dump(),
        )


# Send function execution result
async def send_function_execution_result(
    consumer: AsyncJsonWebsocketConsumer,
    function_execution_result: FunctionExecutionResult,
) -> None:
    """Send a function execution result to the client.

    Args:
        consumer (AsyncJsonWebsocketConsumer): The WebSocket consumer.
        function_execution_result (FunctionExecutionResult): The function execution result to send.
    """

    with suppress(Exception):
        # Send the function execution result to the client
        await consumer.send_json(
            ToolCallExecutionEvent(
                content=[function_execution_result],
                source="server",
                metadata={"error": "false"},
            ).model_dump(),
        )
