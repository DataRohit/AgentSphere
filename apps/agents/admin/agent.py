# Standard library imports

# Third-party imports
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

# Local application imports
from apps.agents.models import Agent


# Admin configuration for the Agent model
@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    """Admin configuration for the Agent model.

    This class defines how the Agent model is displayed and
    can be interacted with in the Django admin interface.

    Attributes:
        list_display (list): Fields to display in the list view.
        list_filter (list): Fields to filter by in the list view.
        search_fields (list): Fields to search in the list view.
        fieldsets (list): Fieldsets to display in the detail view.
        readonly_fields (list): Fields to display in the detail view.
    """

    # Fields to display in the list view
    list_display = [
        "name",
        "type",
        "is_public",
        "organization",
        "user",
        "created_at",
        "avatar_preview",
    ]

    # Fields that can be used for filtering in the admin
    list_filter = ["type", "is_public", "created_at", "organization"]

    # Fields that can be searched
    search_fields = ["name", "description", "type", "user__username", "user__email"]

    # Field sets for the detail view
    fieldsets = [
        (
            _("Basic Information"),
            {
                "fields": ["name", "description", "type"],
            },
        ),
        (
            _("Configuration"),
            {
                "fields": ["system_prompt", "is_public"],
            },
        ),
        (
            _("Relationships"),
            {
                "fields": ["organization", "user"],
            },
        ),
        (
            _("Avatar"),
            {
                "fields": ["avatar_preview"],
                "classes": ["collapse"],
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

    # Fields that are read-only and can't be edited
    readonly_fields = ["created_at", "updated_at", "avatar_preview"]

    # Display a preview of the agent's avatar in the admin
    def avatar_preview(self, obj: Agent) -> str:
        """Display a preview of the agent's avatar in the admin.

        Args:
            obj: The Agent instance

        Returns:
            str: HTML for displaying the avatar image
        """

        # Only show if object has been saved
        if obj.id:
            # Get the avatar URL
            avatar_url = obj.avatar_url()

            # Return the avatar image
            return format_html(
                '<img src="{}" width="100" height="100" style="border-radius: 50%;" />',
                avatar_url,
            )
        return _("Avatar will be available after saving")

    # Short description for the avatar preview
    avatar_preview.short_description = _("Avatar Preview")
