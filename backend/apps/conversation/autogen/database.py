# Standard Library
import uuid
from typing import Any

# Third party imports
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

# Local application imports
from apps.agents.models import Agent
from apps.chats.models import GroupChat, Message, SingleChat
from apps.chats.serializers.message import MessageSerializer
from apps.conversation.models import Session
from apps.llms.models import LLM

# Get the User model
User = get_user_model()


# Get a session from the database
@database_sync_to_async
def get_session(session_id: uuid.UUID | str) -> Session:
    """Get a session from the database.

    Args:
        session_id (uuid.UUID | str): The ID of the session to get.

    Returns:
        Session: The session with the specified ID.

    Raises:
        Session.DoesNotExist: If the session doesn't exist.
    """

    # Get the session from the database with select_related to avoid additional queries
    return Session.objects.select_related("single_chat", "group_chat", "llm").get(id=session_id)


# Deactivate a session in the database
@database_sync_to_async
def deactivate_session(session_id: uuid.UUID | str) -> None:
    """Deactivate a session in the database.

    This method sets the is_active field to False for the specified session.
    The updated_at field will be automatically updated since the Session model
    inherits from TimeStampedModel.

    Args:
        session_id (uuid.UUID | str): The ID of the session to deactivate.
    """

    try:
        # Get the session
        session = Session.objects.get(id=session_id)

        # Set is_active to False
        session.is_active = False

        # Save the session
        session.save()

    # If the session doesn't exist
    except Session.DoesNotExist:
        # Do nothing
        pass


# Get chat information for a session
@database_sync_to_async
def get_chat_info(session_id: uuid.UUID | str) -> dict[str, Any] | None:
    """Get chat information for a session.

    This method safely retrieves the chat type and chat object
    for a session without triggering database queries in async context.

    Args:
        session_id (uuid.UUID | str): The ID of the session.

    Returns:
        dict: A dictionary containing the chat type and chat object.
    """

    try:
        # Get the session with select_related to avoid additional queries
        session = Session.objects.select_related("single_chat", "group_chat").get(id=session_id)

        # If the session has a single chat
        if session.single_chat_id is not None:
            # Return the chat type and chat object
            return {"type": "single", "chat": session.single_chat}

        # If the session has a group chat
        if session.group_chat_id is not None:
            # Return the chat type and chat object
            return {"type": "group", "chat": session.group_chat}

    # If the session doesn't exist
    except Session.DoesNotExist:
        # Return None
        return None

    # If an error occurs
    except (ValueError, TypeError, AttributeError):
        # Return None
        return None

    # Return none
    return None


# Save a message to the database
@database_sync_to_async
def save_message(
    session: Session,
    content: str,
    sender: str,
    user_id: uuid.UUID | None = None,
    agent_id: uuid.UUID | None = None,
) -> dict[str, Any]:
    """Save a message to the database.

    Args:
        session (Session): The session the message belongs to.
        content (str): The content of the message.
        sender (str): The sender of the message.
        user_id (uuid.UUID | None): The ID of the user.
        agent_id (uuid.UUID | None): The ID of the agent.

    Returns:
        dict: The serialized message.
    """

    # Create the message
    message = Message(
        content=content,
        sender=sender,
        user_id=user_id,
        agent_id=agent_id,
        session=session,
    )

    # If the session is a single chat
    if session.single_chat:
        # Set the single chat
        message.single_chat = session.single_chat

        # Set the group chat
        message.group_chat = None

    # If the session is a group chat
    elif session.group_chat:
        # Set the group chat
        message.group_chat = session.group_chat

        # Set the single chat
        message.single_chat = None

    # Save the message
    message.save()

    # Return serialized message
    return MessageSerializer(message).data


# Get an agent from the database
@database_sync_to_async
def get_agent(agent_id: uuid.UUID | str) -> Agent | None:
    """Get an agent from the database.

    Args:
        agent_id (uuid.UUID | str): The ID of the agent to get.

    Returns:
        Agent | None: The agent with the specified ID, or None if not found.
    """

    try:
        # Get and return the agent from the database
        return Agent.objects.get(id=agent_id)

    # If the agent doesn't exist
    except Agent.DoesNotExist:
        # Return None
        return None

    # If an error occurs
    except (ValueError, TypeError, AttributeError):
        # Return None
        return None


# Get the agent ID for a single chat
@database_sync_to_async
def get_agent_id_for_single_chat(chat_id: uuid.UUID | str) -> uuid.UUID | None:
    """Get the agent ID for a single chat.

    This method safely retrieves the agent ID for a single chat
    without triggering database queries in async context.

    Args:
        chat_id (uuid.UUID | str): The ID of the single chat.

    Returns:
        uuid.UUID: The ID of the agent associated with the single chat.
    """

    try:
        # Get the single chat and its agent ID
        chat = SingleChat.objects.only("agent_id").get(id=chat_id)

        if chat.agent_id:
            # Return the agent ID
            return chat.agent_id

    # If the single chat doesn't exist
    except SingleChat.DoesNotExist:
        # Return None
        return None

    # If an error occurs
    except (ValueError, TypeError, AttributeError):
        # Return None
        return None

    # Return None
    return None


# Get all agents for a group chat
@database_sync_to_async
def get_agents_for_group_chat(group_chat_id: uuid.UUID | str) -> list[Agent]:
    """Get all agents for a group chat.

    Args:
        group_chat_id (uuid.UUID | str): The ID of the group chat.

    Returns:
        list: A list of agents participating in the group chat.
    """

    try:
        # Get the agents directly with a prefetch_related to avoid additional queries
        chat = GroupChat.objects.prefetch_related("agents").get(id=group_chat_id)

        # Return the agents
        return list(chat.agents.all())

    # If the group chat doesn't exist
    except GroupChat.DoesNotExist:
        # Return an empty list
        return []

    # If an error occurs
    except (ValueError, TypeError, AttributeError):
        # Return an empty list
        return []

    # Return an empty list
    return []


# Get the LLM details for an agent
@database_sync_to_async
def get_llm_details(agent_id: uuid.UUID | str) -> dict[str, Any] | None:
    """Get the LLM details for an agent.

    This method safely retrieves the LLM details for an agent
    without triggering database queries in async context.

    Args:
        agent_id (uuid.UUID | str): The ID of the agent.

    Returns:
        dict: A dictionary containing the LLM details.
    """

    try:
        # Get the agent with its LLM
        agent = Agent.objects.select_related("llm").get(id=agent_id)

        # Get the LLM details
        return {
            "base_url": agent.llm.base_url,
            "model": agent.llm.model,
            "max_tokens": agent.llm.max_tokens,
            "api_key": agent.llm.get_api_key(),
        }

    # If the agent doesn't exist
    except Agent.DoesNotExist:
        # Return None
        return None

    # If an error occurs
    except (ValueError, TypeError, AttributeError):
        # Return None
        return None

    # Return None
    return None


# Get the LLM details by llm id
@database_sync_to_async
def get_llm_details_by_llm_id(llm_id: uuid.UUID | str) -> dict[str, Any] | None:
    """Get the LLM details by llm id.

    Args:
        llm_id (uuid.UUID | str): The ID of the LLM.

    Returns:
        dict: A dictionary containing the LLM details.
    """

    try:
        # Get the LLM
        llm = LLM.objects.get(id=llm_id)

        # Get the LLM details
        return {
            "base_url": llm.base_url,
            "model": llm.model,
            "max_tokens": llm.max_tokens,
            "api_key": llm.get_api_key(),
        }

    # If the LLM doesn't exist
    except LLM.DoesNotExist:
        # Return None
        return None


# Get previous messages for a session
@database_sync_to_async
def get_previous_messages(session: Session, limit: int = 16) -> list[dict[str, Any]]:
    """Get previous messages for a session.

    This method retrieves the previous messages for a session,
    ordered by creation date (oldest first). It also includes the chat summary
    as the first message to provide context to the agent.

    Args:
        session (Session): The session to get messages for.
        limit (int): The maximum number of messages to retrieve.

    Returns:
        list[dict]: A list of serialized messages, with the chat summary as the first message.
    """

    try:
        # Get the chat summary
        if session.single_chat:
            # Get the chat summary
            summary = session.single_chat.summary

        elif session.group_chat:
            # Get the chat summary
            summary = session.group_chat.summary

        else:
            # Return an empty list if no chat is associated
            return []

        # Get messages for this specific session
        messages = Message.objects.filter(session=session)

        # Order by creation date (oldest first) and limit the number of messages
        messages = messages.order_by("created_at")[:limit]

        # Serialize the messages
        serialized_messages = []

        # If summary exists
        if summary:
            # Add the summary as the first message
            serialized_messages.append({"content": summary, "sender": "agent"})

        # Add the actual messages
        for message in messages:
            # Serialize the message
            serialized = MessageSerializer(message).data

            # Add the serialized message to the list
            serialized_messages.append(serialized)

    # If an error occurs
    except (ValueError, TypeError, AttributeError):
        # Return an empty list
        return []

    # Return the serialized messages
    return serialized_messages
