# Third-party imports
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# Local application imports
from apps.chats.models import GroupChat, Message


# Inline admin for messages in a group chat
class MessageInline(admin.TabularInline):
    """Inline admin for messages in a group chat.

    This inline allows viewing and adding messages directly from the GroupChat admin page.

    Attributes:
        model (Model): The model for the inline.
        extra (int): Number of empty forms to display.
        fk_name (str): The foreign key name to use.
        classes (list): CSS classes for the inline.
        verbose_name (str): Human-readable name for a single instance.
        verbose_name_plural (str): Human-readable plural name.
    """

    # The model for the inline
    model = Message

    # The foreign key to use
    fk_name = "group_chat"

    # Number of empty forms to display
    extra = 1

    # CSS classes for the inline
    classes = ["collapse"]

    # Human-readable name for a single instance
    verbose_name = _("Message")

    # Human-readable plural name
    verbose_name_plural = _("Messages")

    # Fields to display in the inline
    fields = ["sender", "user", "agent", "content"]

    # Fields that need to be prepopulated
    readonly_fields = ["created_at"]


# Admin configuration for the GroupChat model
@admin.register(GroupChat)
class GroupChatAdmin(admin.ModelAdmin):
    """Admin configuration for the GroupChat model.

    This class defines how the GroupChat model is displayed and
    can be interacted with in the Django admin interface.

    Attributes:
        list_display (list): Fields to display in the list view.
        list_filter (list): Fields to filter by in the list view.
        search_fields (list): Fields to search in the list view.
        fieldsets (list): Fieldsets to display in the detail view.
        readonly_fields (list): Fields that cannot be modified.
        inlines (list): Inline models to include.
    """

    # Fields to display in the list view
    list_display = [
        "id",
        "title",
        "organization",
        "user",
        "agent_count",
        "is_public",
        "created_at",
    ]

    # Fields that can be used for filtering in the admin
    list_filter = ["created_at", "organization", "is_public"]

    # Fields that can be searched
    search_fields = [
        "id",
        "title",
        "user__username",
        "user__email",
    ]

    # Field sets for the detail view
    fieldsets = [
        (
            _("Basic Information"),
            {
                "fields": ["title", "is_public", "summary"],
            },
        ),
        (
            _("Relationships"),
            {
                "fields": ["organization", "user", "agents"],
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

    # Inline models to include
    inlines = [MessageInline]

    # Filter for the agents field in the form
    filter_horizontal = ["agents"]

    # Method to get the number of agents in the group chat
    def agent_count(self, obj: GroupChat) -> int:
        """Get the number of agents in the group chat.

        Args:
            obj (GroupChat): The group chat instance.

        Returns:
            int: The number of agents in the group chat.
        """

        # Return the number of agents
        return obj.agents.count()

    # Short description for the agent_count method
    agent_count.short_description = _("Agents")
