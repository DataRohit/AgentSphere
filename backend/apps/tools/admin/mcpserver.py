# Third-party imports
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# Local application imports
from apps.tools.models import MCPServer, MCPTool


# Inline admin for MCPTool model
class MCPToolInline(admin.TabularInline):
    """Inline admin for the MCPTool model.

    This class defines how MCPTool models are displayed inline
    within the MCPServer admin interface.

    Attributes:
        model (MCPTool): The model class.
        extra (int): Number of extra empty forms to display.
    """

    # Model to use for the inline
    model = MCPTool

    # Number of extra empty forms
    extra = 1


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
        inlines (list): Inline models to display in the detail view.
    """

    # Fields to display in the list view
    list_display = [
        "id",
        "name",
        "url",
        "organization",
        "user",
        "created_at",
    ]

    # Fields that can be used for filtering in the admin
    list_filter = ["created_at", "organization", "tags"]

    # Fields that can be searched
    search_fields = ["id", "name", "description", "url", "tags", "user__username", "user__email"]

    # Field sets for the detail view
    fieldsets = [
        (
            _("Basic Information"),
            {
                "fields": ["name", "description", "url", "tags"],
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

    # Inlines
    inlines = [MCPToolInline]
