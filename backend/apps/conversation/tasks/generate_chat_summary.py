# Standard library imports
import asyncio
import uuid

# Third-party imports
from autogen_core.models import UserMessage
from celery import shared_task
from django.db import transaction
from django.db.models import QuerySet

# Local application imports
from apps.chats.models import GroupChat, Message, SingleChat
from apps.conversation.autogen import api_type_to_client
from apps.conversation.models import Session
from apps.llms.models import LLM


# Task to generate a summary for a chat when a session is closed.
@shared_task(name="conversation.generate_chat_summary")
def generate_chat_summary(session_id: str) -> str | None:
    """Generate a summary for a chat when a session is closed.

    This task is triggered when a websocket session is closed. It generates a summary
    of the conversation using the LLM associated with the session.

    Logic:
    - If the summary field is empty: Get all messages and generate a summary
    - If the summary field is present: Get the existing summary + last 16 messages and generate an updated summary

    Args:
        session_id (str): The ID of the session that was closed.

    Returns:
        str | None: The generated summary or None if no summary could be generated.
    """

    try:
        # Convert the session ID to a UUID
        session_uuid = uuid.UUID(session_id)

        # Get the session
        session = Session.objects.get(id=session_uuid)

        # Get the LLM associated with the session
        llm = session.llm

        if not llm:
            # No LLM associated with the session, can't generate summary
            return None

        # If session is for a single chat
        if session.single_chat:
            # Handle single chat summary
            return _generate_single_chat_summary(session, session.single_chat, llm)

        # If session is for a group chat
        if session.group_chat:
            # Handle group chat summary
            return _generate_group_chat_summary(session, session.group_chat, llm)

    except (ValueError, Session.DoesNotExist, LLM.DoesNotExist):
        # Invalid session ID or session/LLM not found
        return None

    # No chat associated with the session
    return None


# Generate a summary for a single chat.
def _generate_single_chat_summary(session: Session, single_chat: SingleChat, llm: LLM) -> str | None:
    """Generate a summary for a single chat.

    Args:
        single_chat (SingleChat): The single chat to generate a summary for.
        llm (LLM): The LLM to use for generating the summary.

    Returns:
        str | None: The generated summary or None if no summary could be generated.
    """

    # Check if the summary field is empty
    if not single_chat.summary:
        # Get all messages for the chat from all sessions
        messages = Message.objects.filter(session__single_chat=single_chat).order_by("created_at")

        # If there are no messages
        if not messages.exists():
            # Return None if no messages exist
            return None

        # Generate a summary using all messages
        summary = _generate_summary_with_llm(messages, llm, None)

    else:
        # Get the existing summary
        existing_summary = single_chat.summary

        # Get the all the messages for the chat from the latest session
        messages = Message.objects.filter(session=session).order_by("-created_at")

        # If there are no messages
        if not messages.exists():
            # Return the existing summary
            return existing_summary

        # Convert to list and reverse to get chronological order
        messages = list(messages)
        messages.reverse()

        # Generate an updated summary
        summary = _generate_summary_with_llm(messages, llm, existing_summary)

    # If a summary was generated
    if summary:
        with transaction.atomic():
            # Update the chat with the new summary
            single_chat.summary = summary

            # Save the chat
            single_chat.save(update_fields=["summary"])

    # Return the generated summary
    return summary


# Generate a summary for a group chat.
def _generate_group_chat_summary(session: Session, group_chat: GroupChat, llm: LLM) -> str | None:
    """Generate a summary for a group chat.

    Args:
        group_chat (GroupChat): The group chat to generate a summary for.
        llm (LLM): The LLM to use for generating the summary.

    Returns:
        str | None: The generated summary or None if no summary could be generated.
    """

    # Check if the summary field is empty
    if not group_chat.summary:
        # Get all messages for the chat from all sessions
        messages = Message.objects.filter(session__group_chat=group_chat).order_by("created_at")

        # If there are no messages
        if not messages.exists():
            # Return None if no messages exist
            return None

        # Generate a summary using all messages
        summary = _generate_summary_with_llm(messages, llm, None)

    else:
        # Get the existing summary
        existing_summary = group_chat.summary

        # Get the all the messages for the chat from the latest session
        messages = Message.objects.filter(session=session).order_by("-created_at")

        # If there are no messages
        if not messages.exists():
            # Return the existing summary
            return existing_summary

        # Convert to list and reverse to get chronological order
        messages = list(messages)
        messages.reverse()

        # Generate an updated summary
        summary = _generate_summary_with_llm(messages, llm, existing_summary)

    # If a summary was generated
    if summary:
        with transaction.atomic():
            # Update the chat with the new summary
            group_chat.summary = summary

            # Save the chat
            group_chat.save(update_fields=["summary"])

    # Return the generated summary
    return summary


# Generate a summary using the specified LLM.
def _generate_summary_with_llm(messages: QuerySet[Message], llm: LLM, existing_summary: str | None) -> str | None:
    """Generate a summary using the specified LLM.

    Args:
        messages (QuerySet): The messages to summarize.
        llm (LLM): The LLM to use for generating the summary.
        existing_summary (Optional[str]): The existing summary, if any.

    Returns:
        str | None: The generated summary or None if no summary could be generated.
    """

    try:
        # List to store the formatted messages
        formatted_messages = []

        # Traverse the messages
        for message in messages:
            # Get the sender type and name
            sender_type = "User" if message.sender == Message.SenderType.USER else "Agent"
            sender_name = message.user.username if message.user else message.agent.name

            # Add the formatted message to the list
            formatted_messages.append(f"{sender_type} ({sender_name}): {message.content}")

        # Join the formatted messages
        messages_text = "\n".join(formatted_messages)

        # Create the prompt synchronously
        if existing_summary:
            # Create the prompt for updating the summary
            prompt = f"""You are tasked with updating a conversation summary based on new messages.

Existing Summary:
{existing_summary}

New Messages:
{messages_text}

Please generate a concise, structured summary of the entire conversation with the following format:

# CONVERSATION SUMMARY

## Topic Overview
* Brief 1-2 sentence overview of what the conversation is about

## Key Points
* Main point 1
* Main point 2
* Main point 3
(Add as many bullet points as needed to capture essential information)

## Details Discussed
* Important fact/information 1
* Important fact/information 2
* Important fact/information 3
(Include specific data, figures, examples mentioned)

## Decisions & Actions
* Decision/conclusion 1
* Action item 1 (with owner if specified)
* Next step 1
(List all agreements, plans, or tasks mentioned)

## Questions & Open Items
* Unresolved question 1
* Follow-up needed on 1
(List any pending items requiring attention)

The summary should be comprehensive enough to understand the conversation without reading the original messages, but focus on brevity and clarity.
"""  # noqa: E501
        else:
            # Create the prompt for creating a summary
            prompt = f"""You are tasked with updating a conversation summary based on new messages.

New Messages:
{messages_text}

Please generate a concise, structured summary of the entire conversation with the following format:

# CONVERSATION SUMMARY

## Topic Overview
* Brief 1-2 sentence overview of what the conversation is about

## Key Points
* Main point 1
* Main point 2
* Main point 3
(Add as many bullet points as needed to capture essential information)

## Details Discussed
* Important fact/information 1
* Important fact/information 2
* Important fact/information 3
(Include specific data, figures, examples mentioned)

## Decisions & Actions
* Decision/conclusion 1
* Action item 1 (with owner if specified)
* Next step 1
(List all agreements, plans, or tasks mentioned)

## Questions & Open Items
* Unresolved question 1
* Follow-up needed on 1
(List any pending items requiring attention)

The summary should be comprehensive enough to understand the conversation without reading the original messages, but focus on brevity and clarity.
"""  # noqa: E501

        # Define the async function
        async def _generate_summary_async():
            # Get the client for the LLM
            model_client = api_type_to_client[llm.api_type](
                model=llm.model,
                api_key=llm.get_api_key(),
                max_tokens=32_768,
            )

            # Generate the summary
            response = await model_client.create([UserMessage(content=prompt, source="user")])

            # Close the client
            await model_client.close()

            # Return the generated summary
            if response and hasattr(response, "content"):
                # Return the content of the response
                return response.content

            # Return None if no response was generated
            return None

        # Run the async function in a new event loop
        loop = asyncio.new_event_loop()

        # Run the async function
        summary = loop.run_until_complete(_generate_summary_async())

        # Close the loop
        loop.close()

    except (TimeoutError, ConnectionError, ValueError, KeyError, AttributeError):
        # Return None if an error occurred
        return None

    # Return the generated summary
    return summary
