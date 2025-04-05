# Third-party imports
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

# Project imports
from .forms import UserChangeForm, UserCreationForm
from .models import UserActivationToken, UserDeletionToken, UserPasswordResetToken

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
        "email",
        "first_name",
        "last_name",
        "username",
        "is_active",
        "is_superuser",
    ]

    # Fields that link to the detail view
    list_display_links = ["id", "email", "username"]

    # Fields to search in the admin interface
    search_fields = ["email", "first_name", "last_name"]

    # Default ordering for the list view
    ordering = ["id"]

    # Field grouping for the detail view
    fieldsets = (
        (_("Login Credentials"), {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "username")}),
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
                    "password1",
                    "password2",
                ),
            },
        ),
    )


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


# Admin interface for UserDeletionToken model
@admin.register(UserDeletionToken)
class UserDeletionTokenAdmin(admin.ModelAdmin):
    """Admin interface for the UserDeletionToken model.

    Provides custom admin functionality for managing user deletion tokens.

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


# Admin interface for UserPasswordResetToken model
@admin.register(UserPasswordResetToken)
class UserPasswordResetTokenAdmin(admin.ModelAdmin):
    """Admin interface for the UserPasswordResetToken model.

    Provides custom admin functionality for managing user password reset tokens.

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
