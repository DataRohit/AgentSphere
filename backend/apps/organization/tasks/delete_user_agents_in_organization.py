# Standard library imports
from uuid import UUID

# Third-party imports
from celery import shared_task
from django.db import transaction

# Project imports
from apps.agents.models import Agent


# Delete user agents in organization task
@shared_task(name="organization.delete_user_agents_in_organization")
def delete_user_agents_in_organization(user_id: UUID, organization_id: UUID) -> int:
    """Delete all agents created by a user in an organization.

    This task is used when a user leaves an organization to clean up their agents
    in that organization.

    Args:
        user_id (UUID): The ID of the user whose agents should be deleted.
        organization_id (UUID): The ID of the organization the user is leaving.

    Returns:
        int: The number of agents deleted.
    """

    # Get agents created by the user in the specified organization
    agents = Agent.objects.filter(
        user_id=user_id,
        organization_id=organization_id,
    )

    # Get the count of agents to be deleted
    deleted_count = agents.count()

    # If there are no agents to delete
    if deleted_count == 0:
        # Return early
        return 0

    # Delete agents in a transaction
    with transaction.atomic():
        # Bulk delete agents
        agents.delete()

    # Return the number of agents deleted
    return deleted_count
