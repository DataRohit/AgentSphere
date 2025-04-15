# Third-party imports
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

# Local application imports
from apps.users.forms import UserChangeForm, UserCreationForm

# Get the User model
User = get_user_model()


# Custom admin interface for User model
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin interface for the User model.

    Extends Django's base UserAdmin to provide custom admin functionality
    for user management in the admin interface.

    Attributes:
        form (UserChangeForm): Form for modifying existing users.
        add_form (UserCreationForm): Form for creating new users.
        list_display (list): Fields to display in the admin list view.
        list_display_links (list): Fields that link to the detail view.
        search_fields (list): Fields to search in the admin interface.
        ordering (list): Default ordering for the list view.
        fieldsets (tuple): Field grouping for the detail view.
        add_fieldsets (tuple): Field grouping for the add view.
    """

    # Form for modifying existing users
    form = UserChangeForm

    # Form for creating new users
    add_form = UserCreationForm

    # Fields to display in the list view
    list_display = [
        "id",
        "display_avatar",
        "email",
        "first_name",
        "last_name",
        "username",
        "is_active",
        "is_superuser",
    ]

    # Fields that link to the detail view
    list_display_links = ["id", "display_avatar", "email", "username"]

    # Fields to search in the admin interface
    search_fields = ["email", "first_name", "last_name"]

    # Default ordering for the list view
    ordering = ["id"]

    # Fields that cannot be modified
    readonly_fields = ["display_avatar", "last_login", "date_joined"]

    # Field grouping for the detail view
    fieldsets = (
        (_("Login Credentials"), {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "username",
                    "avatar",
                    "display_avatar",
                ),
            },
        ),
        (
            _("Permissions and Groups"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important Dates"), {"fields": ("last_login", "date_joined")}),
    )

    # Field grouping for the add view
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "avatar",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    # Display the user avatar in the admin interface
    def display_avatar(self, obj: User) -> str:
        """Display the user avatar in the admin interface.

        Args:
            obj (User): The user instance.

        Returns:
            str: HTML for displaying the avatar.
        """

        # Return the avatar URL
        return format_html('<img src="{}" width="50" height="50" />', obj.avatar_url)

    # Short description for the avatar field
    display_avatar.short_description = _("Avatar")
