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
        "id",
        "name",
        "llm",
        "organization",
        "user",
        "created_at",
    ]

    # Fields that can be used for filtering in the admin
    list_filter = ["created_at", "organization", "llm__api_type"]

    # Fields that can be searched
    search_fields = [
        "name",
        "description",
        "user__username",
        "user__email",
        "llm__model",
    ]

    # Field sets for the detail view
    fieldsets = [
        (
            _("Basic Information"),
            {
                "fields": ["name", "description"],
            },
        ),
        (
            _("Configuration"),
            {
                "fields": ["system_prompt", "llm"],
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

    # Define autocomplete fields for better performance with large datasets
    autocomplete_fields = ["llm"]

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

        # Return a placeholder if the avatar is not set
        return _("Avatar will be available after saving")

    # Short description for the avatar preview
    avatar_preview.short_description = _("Avatar Preview")

    # Custom save method to ensure organization and user consistency
    def save_model(self, request, obj, form, change):
        """Custom save method for Agent model.

        Ensures that when an agent is saved, the organization and user
        are consistent with its associated LLM.

        Args:
            request: The request object
            obj: The Agent instance
            form: The form instance
            change: Boolean indicating if this is an edit
        """

        # If LLM is set, ensure organization and user are consistent
        if obj.llm:
            # Set organization based on LLM if not already set
            if not obj.organization and obj.llm.organization:
                obj.organization = obj.llm.organization

            # Set user based on LLM if not already set
            if not obj.user and obj.llm.user:
                obj.user = obj.llm.user

        # Save the agent
        super().save_model(request, obj, form, change)
