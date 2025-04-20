# Third-party imports
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

# Local application imports
from apps.llms.models import LLM


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
        "has_api_key",
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
                "fields": ["api_key", "api_key_status", "max_tokens"],
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
    readonly_fields = ["created_at", "updated_at", "api_key_status"]

    # Check if an LLM instance has an API key stored in Vault
    def has_api_key(self, obj):
        """Check if an LLM instance has an API key stored in Vault.

        Args:
            obj (LLM): The LLM instance to check.

        Returns:
            str: HTML checkmark or cross icon indicating whether the API key exists.
        """

        # Check if the API key exists
        api_key = obj.get_api_key()
        if api_key:
            # Return a checkmark
            return format_html('<span style="color: green;">✓</span>')

        # Return a cross icon
        return format_html('<span style="color: red;">✗</span>')

    # Short description for the has_api_key field
    has_api_key.short_description = _("API Key")

    # Display the status of the API key in Vault
    def api_key_status(self, obj: LLM) -> str:
        """Display the status of the API key in Vault.

        Args:
            obj (LLM): The LLM instance to check.

        Returns:
            str: HTML formatted status of the API key.
        """

        # Not saved yet
        if not obj.pk:
            return format_html(
                '<span style="color: gray;">Save to store API key</span>',
            )

        # API key stored in Vault
        api_key = obj.get_api_key()
        if api_key:
            # Mask the API key
            masked_key = (
                f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}"
                if len(api_key) > 8  # noqa: PLR2004
                else "****"
            )

            # Return a checkmark
            return format_html(
                '<span style="color: green;">API key stored securely in Vault: {}</span>',
                masked_key,
            )

        # No API key stored in Vault
        return format_html(
            '<span style="color: red;">No API key stored in Vault</span>',
        )

    # Short description for the api_key_status field
    api_key_status.short_description = _("API Key Status")
