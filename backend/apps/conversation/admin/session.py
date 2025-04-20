# Third-party imports
from django.contrib import admin

# Local application imports
from apps.conversation.models import Session


# Admin configuration for the Session model
@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    """Admin configuration for the Session model.

    This class defines how the Session model is displayed and
    can be interacted with in the Django admin interface.

    Attributes:
        list_display (list): Fields to display in the list view.
        list_filter (list): Fields to filter by in the list view.
        search_fields (list): Fields to search in the list view.
        readonly_fields (list): Fields that cannot be modified.
        fieldsets (list): Fieldsets to display in the detail view.
    """

    # Fields to display in the list view
    list_display = [
        "id",
        "get_chat_title",
        "chat_type",
        "is_active",
        "llm",
        "created_at",
        "updated_at",
    ]

    # Fields to filter by in the list view
    list_filter = [
        "is_active",
        "llm",
        "created_at",
        "updated_at",
    ]

    # Fields to search in the list view
    search_fields = [
        "id",
        "single_chat__title",
        "group_chat__title",
    ]

    # Fields that cannot be modified
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
    ]

    # Fieldsets to display in the detail view
    fieldsets = [
        (
            "Session Information",
            {
                "fields": [
                    "id",
                    "single_chat",
                    "group_chat",
                    "is_active",
                ],
            },
        ),
        (
            "LLM Configuration",
            {
                "fields": [
                    "llm",
                    "selector_prompt",
                ],
            },
        ),
        (
            "Timestamps",
            {
                "fields": [
                    "created_at",
                    "updated_at",
                ],
            },
        ),
    ]

    # Custom method to get the chat title
    def get_chat_title(self, obj: Session) -> str:
        """Get the title of the chat associated with this session.

        Args:
            obj (Session): The session instance.

        Returns:
            str: The title of the associated chat.
        """

        # If the session is linked to a single chat
        if obj.single_chat:
            # Return the single chat title
            return obj.single_chat.title

        # If the session is linked to a group chat
        if obj.group_chat:
            # Return the group chat title
            return obj.group_chat.title

        # If the session is not linked to a single chat or group chat
        return "-"

    # Set the column name for the get_chat_title method
    get_chat_title.short_description = "Chat Title"

    # Custom method to get the chat type
    def chat_type(self, obj: Session) -> str:
        """Get the type of chat associated with this session.

        Args:
            obj (Session): The session instance.

        Returns:
            str: The type of the associated chat.
        """

        # If the session is linked to a single chat
        if obj.single_chat:
            # Return the single chat type
            return "Single Chat"

        # If the session is linked to a group chat
        if obj.group_chat:
            # Return the group chat type
            return "Group Chat"

        # If the session is not linked to a single chat or group chat
        return "-"

    # Set the column name for the chat_type method
    chat_type.short_description = "Chat Type"
