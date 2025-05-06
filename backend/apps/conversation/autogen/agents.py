# Standard library imports
import logging
from collections.abc import Callable
from contextlib import suppress
from typing import Any

# Third party imports
import slugify
from asgiref.sync import sync_to_async
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import TextMessage, UserInputRequestedEvent
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_core.memory import ListMemory, MemoryContent
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Local application imports
from apps.agents.models import Agent
from apps.conversation.autogen.database import get_llm_details, get_llm_details_by_llm_id
from apps.conversation.autogen.mcp import get_mcp_tools_for_agent
from apps.conversation.models import Session

# Disable autogen and SSE logging
for logger_name in [
    # Autogen loggers
    "autogen_agentchat",
    "autogen_core",
    "_single_threaded_agent_runtime",
    "autogen_runtime_core",
    "autogen_agentchat.teams",
    "autogen_agentchat.agents",
    # SSE loggers
    "sse",
    "mcp.client.sse",
    "mcp.client.session",
    "autogen_ext.tools.mcp",
]:
    # Initialize the logger
    logger = logging.getLogger(logger_name)

    # Set the logger level to critical (only show critical errors)
    logger.setLevel(logging.CRITICAL)

    # Set the logger propagate to false (don't pass messages to parent loggers)
    logger.propagate = False


# Setup agent memory
async def setup_agent_memory(
    agent_id: int,
    previous_messages: list[dict[str, Any]],
) -> tuple[ListMemory, BufferedChatCompletionContext]:
    """Set up memory and context for an agent.

    Args:
        agent_id (int): The ID of the agent.
        previous_messages (list[dict[str, Any]]): Previous messages to add to memory.

    Returns:
        tuple[ListMemory, BufferedChatCompletionContext]: The memory and context objects.
    """

    # Create a memory for the agent
    agent_memory = ListMemory(name=f"agent_{agent_id}_memory")

    # Create a model context with memory
    model_context = BufferedChatCompletionContext(buffer_size=32)

    # Add previous messages to memory
    added_messages = 0
    for msg in previous_messages:
        # If the message is a system message or doesn't have content
        if not msg.get("content") or msg.get("sender") not in ("user", "agent"):
            # Skip the message
            continue

        with suppress(ValueError, TypeError, AttributeError):
            # Create a memory content from the message
            content = f"{msg.get('sender')}: {msg.get('content')}"
            memory_content = MemoryContent(
                content=content,
                mime_type="text/plain",
            )

            # Add to memory
            await agent_memory.add(memory_content)

            # Increment the counter
            added_messages += 1

    # Update the model context with memory
    with suppress(Exception):
        await agent_memory.update_context(model_context)

    # Return the memory and context
    return agent_memory, model_context


def create_chat_completion_client(
    base_url: str,
    llm_model: str,
    llm_api_key: str | None = None,
    llm_max_tokens: int | None = None,
) -> Any:
    """Create a chat completion client using OpenAIChatCompletionClient.

    Args:
        base_url (str): The base URL for the LLM API.
        llm_model (str): The model name.
        llm_api_key (str | None): The API key for the LLM.
        llm_max_tokens (int | None): Max tokens for completion.

    Returns:
        Any: A chat completion client instance.
    """

    # Create the chat completion client
    with suppress(Exception):
        return OpenAIChatCompletionClient(
            model=llm_model,
            base_url=base_url,
            api_key=llm_api_key or "placeholder",
            max_tokens=llm_max_tokens,
        )

    # Return None if there was an exception
    return None


# Setup Autogen agents
async def setup_autogen_agents(agents: list[Agent], previous_messages: list[dict[str, Any]]) -> list[Any]:
    """Set up Autogen agents from Django Agent models.

    Args:
        agents (list[Agent]): List of Agent models.
        previous_messages (list[dict[str, Any]]): Previous messages for context.

    Returns:
        list[Any]: List of Autogen agent instances.
    """

    # List of Autogen agents
    autogen_agents = []

    # Traverse the agents
    for agent in agents:
        with suppress(Exception):
            # Get the agent details
            agent_name = agent.name
            agent_description = agent.description
            agent_system_prompt = agent.system_prompt

            # Get the LLM details from database
            llm_details = await get_llm_details(agent.id)

            # If the LLM details are not found
            if not llm_details:
                # Skip this iteration
                continue

            # Extract LLM details
            base_url = llm_details["base_url"]
            llm_model = llm_details["model"]
            llm_max_tokens = llm_details["max_tokens"]
            llm_api_key = llm_details["api_key"]

            # Create the chat completion client
            chat_completion_client = create_chat_completion_client(base_url, llm_model, llm_api_key, llm_max_tokens)

            # If the chat completion client is not created
            if not chat_completion_client:
                # Skip this iteration
                continue

            # Set up memory and context
            agent_memory, model_context = await setup_agent_memory(agent.id, previous_messages)

            # Get MCP tools for the agent
            mcp_tools = await get_mcp_tools_for_agent(agent.id)

            # Enhance the system prompt with instructions to maintain context
            enhanced_system_prompt = (
                f"{agent_system_prompt}\n\n"
                "IMPORTANT: Maintain context of the conversation. "
                "Remember previous messages and refer to them when appropriate. "
                "Be consistent with your previous responses."
            )

            # If there are MCP tools
            if mcp_tools:
                # Add information about available tools
                enhanced_system_prompt += (
                    "\n\nYou have access to external tools. Use them when appropriate to fulfill user requests."
                )

            # Create assistant agent & add to the list
            agent_slug = slugify.slugify(agent_name)

            # Initialize the assistant agent with tools if available
            assistant_agent = AssistantAgent(
                name=agent_slug,
                description=agent_description,
                model_client=chat_completion_client,
                system_message=enhanced_system_prompt,
                model_context=model_context,
                tools=mcp_tools if mcp_tools else None,
                reflect_on_tool_use=True,
            )

            # Add the agent to the list
            autogen_agents.append(assistant_agent)

    # Create user proxy agent
    user_proxy = UserProxyAgent("user")

    # Add the user proxy agent to the autogen agents
    autogen_agents.append(user_proxy)

    # Return the list of agents
    return autogen_agents


async def _create_chat_team(
    chat_type: str,
    autogen_agents: list[Agent],
    session: Session,
    agents: list[Agent],
) -> tuple[Any, list[tuple[int, str, str]] | None]:
    """Create a chat team based on chat type.

    Args:
        chat_type (str): The type of chat (single, group).
        autogen_agents (list[Agent]): List of autogen agent instances.
        session (Session): The session object containing LLM and other settings.
        agents (list[Agent]): List of agent models.

    Returns:
        tuple[Any, list[tuple[int, str, str]] | None]: The team object and error response (if any).
    """

    # Set the termination conditions
    text_mention_termination = TextMentionTermination("TERMINATE")
    max_messages_termination = MaxMessageTermination(max_messages=8)
    termination = text_mention_termination | max_messages_termination

    # If the chat type is single
    if chat_type == "single":
        # Create round robin group chat
        return RoundRobinGroupChat(participants=autogen_agents, termination_condition=termination), None

    # If chat type is group
    if chat_type == "group":
        try:
            # Get session llm details
            llm_details = await get_llm_details_by_llm_id(session.llm.id)

            # Initialize the model client
            model_client = create_chat_completion_client(
                llm_details["base_url"],
                llm_details["model"],
                llm_details["api_key"],
                llm_details["max_tokens"],
            )

            # Create the selector group chat using sync_to_async
            create_selector_chat = sync_to_async(SelectorGroupChat)
            team = await create_selector_chat(
                participants=autogen_agents,
                model_client=model_client,
                termination_condition=termination,
            )

        except (ValueError, TypeError, AttributeError) as e:
            # If agents in list
            if agents:
                # Return the error
                return None, [(agents[0].id, "agent", f"I encountered an error setting up the group chat: {e!s}")]

            # Return an empty list
            return None, []

        # Return the team & error
        return team, None

    # Invalid chat type
    return None, []


# Process message stream
async def _process_message_stream(
    stream: Any,
    agents: list[Agent],
    message_callback: Callable | None = None,
) -> list[tuple[int, str, str]]:
    """Process message stream and collect agent responses.

    Args:
        stream: The message stream to process.
        agents (list[Agent]): List of agent models.
        message_callback (Optional[Callable], optional): Callback function to process each message as it arrives.
            The callback should accept (agent_id, source, content) as parameters.

    Returns:
        list[tuple[int, str, str]]: A list of tuples containing agent responses.
    """

    # List of agent responses
    agent_responses = []

    # Process the message stream
    async for message in stream:
        # If message is task result
        if isinstance(message, TaskResult):
            continue

        # If message is user input request
        if isinstance(message, UserInputRequestedEvent):
            break

        # If it is an agent's response
        if message.source != "user":
            # Initialize the agent found flag
            agent_found = False

            # Initialize the agent id
            agent_id = None

            # Set the message source & content
            source = message.source
            content = message.content

            # Traverse over the agents
            for agent in agents:
                # Slugify the agent name
                agent_slug = slugify.slugify(agent.name)

                # If the message source is the agent's name or "agent"
                if message.source in (agent_slug, "agent"):
                    # Set the agent ID
                    agent_id = agent.id

                    # Mark the agent as found
                    agent_found = True

                    # Break the loop
                    break

            # If no agent was found
            if not agent_found and agents:
                # Use the first agent as fallback agent
                agent_id = agents[0].id

            # Create the response tuple
            response_tuple = (agent_id, source, content)

            # Add to the list of responses
            agent_responses.append(response_tuple)

            # If a callback was provided
            if message_callback and agent_id:
                # Call the callback function with message
                await message_callback(*response_tuple)

    # Return the list of agent responses
    return agent_responses


# Process the user message with the agents and get the response
async def process_with_agents(  # noqa: PLR0911
    chat_type: str,
    session: Session,
    user_message: str,
    agents: list[Agent],
    params: dict[str, Any] | None = None,
) -> list[tuple[int, str, str]]:
    """Process the user message with the agents and get the response.

    Args:
        chat_type (str): The type of chat (single, group).
        session (Session): The session object containing LLM and other settings.
        user_message (str): The user message to process.
        agents (list[Agent]): List of agent models.
        params (Optional[Dict[str, Any]], optional): Additional parameters including:
            - previous_messages (list[dict[str, Any]]): Previous messages for context.
            - message_callback (callable): Callback for processing each message as it arrives.

    Returns:
        list[tuple[int, str, str]]: A list of tuples containing the agent ID, source, and the response content.
    """

    # Extract parameters from params dict
    params = params or {}
    previous_messages = params.get("previous_messages", [])
    message_callback = params.get("message_callback", None)

    # Default response for empty agents or errors
    default_response = []

    # If agents in list
    if agents:
        # Set default response
        default_response = [(agents[0].id, "agent", "I'm sorry, I couldn't process your request at this time.")]

    try:
        # Set up Autogen agents
        autogen_agents = await setup_autogen_agents(agents, previous_messages)

        # If no valid agents were created
        if len(autogen_agents) <= 1:
            # Return default response
            return default_response if agents else []

        # Create team based on chat type
        team, error_response = await _create_chat_team(chat_type, autogen_agents, session, agents)

        # If there was an error creating the team
        if error_response:
            # Return error response
            return error_response

        # If team was not created
        if not team:
            # Return empty list
            return []

        # Create the message
        message = TextMessage(content=user_message, source="user")

        # Start the stream
        stream = team.run_stream(task=message)

        # Process the message stream
        agent_responses = await _process_message_stream(stream, agents, message_callback)

        # If no responses were collected but we have agents
        if not agent_responses and agents:
            # Return the default response
            return default_response

    except (ValueError, TypeError, AttributeError) as e:
        # If we have agents
        if agents:
            # Return the default message
            return [(agents[0].id, "agent", f"I encountered an error while processing your request: {e!s}")]

        # Return empty list
        return []

    # Return agent response
    return agent_responses
