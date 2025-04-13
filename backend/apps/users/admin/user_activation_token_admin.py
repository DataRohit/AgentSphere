# Third-party imports
from django.contrib import admin

# Project imports
from apps.users.models import UserActivationToken


# Admin interface for UserActivationToken model
@admin.register(UserActivationToken)
class UserActivationTokenAdmin(admin.ModelAdmin):
    """Admin interface for the UserActivationToken model.

    Provides custom admin functionality for managing user activation tokens.

    Attributes:
        list_display (list): Fields to display in the admin list view.
        list_display_links (list): Fields that link to the detail view.
        search_fields (list): Fields to search in the admin interface.
        list_filter (list): Fields to filter by in the admin interface.
        readonly_fields (list): Fields that cannot be modified.
        date_hierarchy (str): Field to use for date-based navigation.
    """

    # Fields to display in the list view
    list_display = [
        "id",
        "user",
        "uid",
        "token",
        "expires_at",
        "is_expired",
        "created_at",
    ]

    # Fields that link to the detail view
    list_display_links = ["id", "user"]

    # Fields to search in the admin interface
    search_fields = ["user__email", "user__username", "uid", "token"]

    # Fields to filter by in the admin interface
    list_filter = ["created_at", "expires_at"]

    # Fields that cannot be modified
    readonly_fields = ["is_expired"]

    # Field to use for date-based navigation
    date_hierarchy = "created_at"
