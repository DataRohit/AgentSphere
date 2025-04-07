# Third-party imports
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# Local application imports
from apps.agents.models import LLM


# Admin configuration for the LLM model
@admin.register(LLM)
class LLMAdmin(admin.ModelAdmin):
    """Admin configuration for the LLM model.

    This class defines how the LLM model is displayed and
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
        "api_type",
        "model",
        "max_tokens",
        "organization",
        "user",
        "created_at",
    ]

    # Fields that can be used for filtering in the admin
    list_filter = ["api_type", "created_at", "organization"]

    # Fields that can be searched
    search_fields = ["id", "api_type", "model", "user__username", "user__email"]

    # Field sets for the detail view
    fieldsets = [
        (
            _("Basic Information"),
            {
                "fields": ["api_type", "model"],
            },
        ),
        (
            _("Configuration"),
            {
                "fields": ["api_key", "max_tokens"],
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

    # Fields that are read-only and can't be edited
    readonly_fields = ["created_at", "updated_at"]

    # Enable search for this model in admin autocomplete widgets
