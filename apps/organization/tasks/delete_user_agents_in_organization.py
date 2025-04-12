# Standard library imports
from uuid import UUID

# Third-party imports
from celery import shared_task

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

    # Delete agents created by the user in the specified organization
    deleted_count, _ = Agent.objects.filter(
        user_id=user_id,
        organization_id=organization_id,
    ).delete()

    # Return the number of agents deleted
    return deleted_count
