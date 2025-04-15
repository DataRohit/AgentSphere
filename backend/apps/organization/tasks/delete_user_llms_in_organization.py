# Standard library imports
from concurrent.futures import ThreadPoolExecutor
from uuid import UUID

# Third-party imports
from celery import shared_task
from django.db import transaction

# Local application imports
from apps.common.utils.vault import delete_api_key
from apps.llms.models import LLM


# Delete user LLMs in organization task
@shared_task(name="organization.delete_user_llms_in_organization")
def delete_user_llms_in_organization(user_id: UUID, organization_id: UUID) -> int:
    """Delete all LLM configurations created by a user in an organization.

    This task is used when a user leaves an organization to clean up their LLM configurations
    in that organization.

    Args:
        user_id (UUID): The ID of the user whose LLM configurations should be deleted.
        organization_id (UUID): The ID of the organization the user is leaving.

    Returns:
        int: The number of LLM configurations deleted.
    """

    # Get LLM configurations created by the user in the specified organization
    llms = LLM.objects.filter(
        user_id=user_id,
        organization_id=organization_id,
    )

    # Get the count of LLMs to be deleted
    deleted_count = llms.count()

    # If there are no LLMs to delete
    if deleted_count == 0:
        # Return early
        return 0

    # Get the IDs of LLMs that need API key deletion from Vault
    llm_ids_with_api_keys = list(
        llms.exclude(api_type="ollama").values_list("id", flat=True),
    )

    # Function to delete API keys in parallel
    def delete_api_keys_in_parallel(llm_ids):
        # If no LLM IDs are provided
        if not llm_ids:
            # Return early
            return

        # Use ThreadPoolExecutor to delete API keys in parallel without a for loop
        with ThreadPoolExecutor(max_workers=min(8, len(llm_ids))) as executor:
            # Map the delete_api_key function to each LLM ID
            executor.map(lambda llm_id: delete_api_key("llm", str(llm_id)), llm_ids)

    # Delete LLMs and API keys in a transaction
    with transaction.atomic():
        # Delete all LLMs in a single bulk operation for efficiency
        llms.delete()

        # Delete API keys from Vault for Gemini LLMs in parallel
        delete_api_keys_in_parallel(llm_ids_with_api_keys)

    # Return the number of LLM configurations deleted
    return deleted_count
