# Standard library imports
from uuid import UUID

# Third-party imports
from celery import shared_task
from django.db import transaction

# Local application imports
from apps.chats.models import Message


# Delete group chat messages task
@shared_task(name="chats.delete_group_chat_messages")
def delete_group_chat_messages(group_chat_id: UUID) -> int:
    """Delete all messages associated with a group chat.

    This task is used when a group chat is deleted to clean up all associated messages.
    It performs a bulk delete operation for efficiency.

    Args:
        group_chat_id (UUID): The ID of the group chat whose messages should be deleted.

    Returns:
        int: The number of messages deleted.
    """

    # Get messages associated with the group chat
    messages = Message.objects.filter(
        group_chat_id=group_chat_id,
    )

    # Get the count of messages to be deleted
    deleted_count = messages.count()

    # If there are no messages to delete
    if deleted_count == 0:
        # Return early
        return 0

    # Delete messages in a transaction
    with transaction.atomic():
        # Bulk delete messages
        messages.delete()

    # Return the number of messages deleted
    return deleted_count
