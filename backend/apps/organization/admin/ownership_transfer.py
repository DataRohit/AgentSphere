# Third-party imports
from django.contrib import admin

# Project imports
from apps.organization.models import OrganizationOwnershipTransfer


# Admin for OrganizationOwnershipTransfer
@admin.register(OrganizationOwnershipTransfer)
class OrganizationOwnershipTransferAdmin(admin.ModelAdmin):
    """Admin for OrganizationOwnershipTransfer model.

    Attributes:
        list_display (tuple): Fields to display in the list view.
        list_filter (tuple): Fields to filter the list view by.
        search_fields (tuple): Fields to search in.
        readonly_fields (tuple): Fields that cannot be edited.
    """

    # Fields to display in the list view
    list_display = (
        "id",
        "organization",
        "current_owner",
        "new_owner",
        "expiration_time",
        "is_active",
        "is_accepted",
        "is_rejected",
        "is_expired",
        "is_cancelled",
        "created_at",
        "updated_at",
    )

    # Fields to filter the list view by
    list_filter = (
        "is_accepted",
        "is_rejected",
        "is_expired",
        "is_cancelled",
        "created_at",
        "updated_at",
    )

    # Fields to search in
    search_fields = (
        "id__iexact",
        "organization__name__icontains",
        "current_owner__email__icontains",
        "new_owner__email__icontains",
    )

    # Fields that cannot be edited
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
