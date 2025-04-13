# Third-party imports
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

# Project imports
from apps.organization.models import Organization


# Admin interface for Organization model
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin interface for the Organization model.

    Provides custom admin functionality for managing organizations.

    Attributes:
        list_display (list): Fields to display in the admin list view.
        list_display_links (list): Fields that link to the detail view.
        search_fields (list): Fields to search in the admin interface.
        list_filter (list): Fields to filter by in the admin interface.
        readonly_fields (list): Fields that cannot be modified.
        date_hierarchy (str): Field to use for date-based navigation.
        fieldsets (tuple): Field grouping for the detail view.
    """

    # Fields to display in the list view
    list_display = [
        "id",
        "name",
        "owner",
        "display_logo",
        "member_count",
        "is_active",
        "created_at",
    ]

    # Fields that link to the detail view
    list_display_links = ["id", "name"]

    # Fields to search in the admin interface
    search_fields = ["name", "owner__email", "owner__username"]

    # Fields to filter by in the admin interface
    list_filter = ["is_active", "created_at"]

    # Fields that cannot be modified
    readonly_fields = ["member_count", "display_logo", "created_at", "updated_at"]

    # Field to use for date-based navigation
    date_hierarchy = "created_at"

    # Field grouping for the detail view
    fieldsets = (
        (
            _("Organization Information"),
            {"fields": ("name", "description", "logo", "display_logo", "website")},
        ),
        (_("Ownership and Status"), {"fields": ("owner", "is_active")}),
        (_("Members"), {"fields": ("members",)}),
        (
            _("Important Dates"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    # Get the number of members in the organization
    def member_count(self, obj: Organization) -> int:
        """Get the number of members in the organization.

        Args:
            obj (Organization): The organization instance.

        Returns:
            int: The count of members in the organization.
        """

        # Return the number of members
        return obj.members.count()

    # Set the column name for the member_count field
    member_count.short_description = _("Member Count")

    # Display the organization logo in the admin interface
    def display_logo(self, obj: Organization) -> str:
        """Display the organization logo in the admin interface.

        Args:
            obj (Organization): The organization instance.

        Returns:
            str: HTML for displaying the logo.
        """

        # Return the logo URL
        return format_html('<img src="{}" width="50" height="50" />', obj.logo_url)

    # Set the column name for the display_logo field
    display_logo.short_description = _("Logo")
