# Third-party imports
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# Local application imports
from apps.tools.models import MCPServer


# Admin configuration for the MCPServer model
@admin.register(MCPServer)
class MCPServerAdmin(admin.ModelAdmin):
    """Admin configuration for the MCPServer model.

    This class defines how the MCPServer model is displayed and
    can be interacted with in the Django admin interface.

    Attributes:
        list_display (list): Fields to display in the list view.
        list_filter (list): Fields to filter by in the list view.
        search_fields (list): Fields to search in the list view.
        fieldsets (list): Fieldsets to display in the detail view.
        readonly_fields (list): Fields to display as read-only in the detail view.
    """

    # Fields to display in the list view
    list_display = [
        "id",
        "name",
        "tool_name",
        "url",
        "organization",
        "user",
        "created_at",
    ]

    # Fields that can be used for filtering in the admin
    list_filter = ["created_at", "organization", "tags"]

    # Fields that can be searched
    search_fields = ["id", "name", "tool_name", "description", "url", "tags", "user__username", "user__email"]

    # Field sets for the detail view
    fieldsets = [
        (
            _("Basic Information"),
            {
                "fields": ["name", "tool_name", "description", "url", "tags"],
            },
        ),
        (
            _("Relationships"),
            {
                "fields": ["organization", "user"],
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]

    # Fields that cannot be modified
    readonly_fields = ["created_at", "updated_at"]
