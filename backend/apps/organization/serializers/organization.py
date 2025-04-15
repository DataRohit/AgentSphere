# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

# Local application imports
from apps.organization.models import Organization
from apps.users.serializers import UserDetailSerializer


# Organization serializer
class OrganizationSerializer(serializers.ModelSerializer):
    """Organization serializer.

    This serializer provides a representation of the Organization model.

    Attributes:
        id (UUID): The organization's ID.
        name (str): The organization's name.
        description (str): The organization's description.
        website (str): The organization's website.
        logo_url (str): The URL to the organization's logo.
        owner (UserDetailSerializer): The owner of the organization.
        member_count (int): The number of members in the organization.

        created_at (datetime): The date and time the organization was created.
        updated_at (datetime): The date and time the organization was last updated.

    Meta:
        model (Organization): The model class.
        fields (list): The fields to include in the serializer.
        read_only_fields (list): Fields that are read-only.
    """

    # Logo URL field
    logo_url = serializers.URLField(
        read_only=True,
        help_text=_("URL to the organization's logo."),
    )

    # Member count field
    member_count = serializers.IntegerField(
        read_only=True,
        help_text=_("Number of members in the organization."),
    )

    # Owner serializer
    owner = UserDetailSerializer(read_only=True)

    # Meta class for OrganizationSerializer configuration
    class Meta:
        """Meta class for OrganizationSerializer configuration.

        Attributes:
            model (Organization): The model class.
            fields (list): The fields to include in the serializer.
            read_only_fields (list): Fields that are read-only.
        """

        # Model to use for the serializer
        model = Organization

        # Fields to include in the serializer
        fields = [
            "id",
            "name",
            "description",
            "website",
            "logo_url",
            "owner",
            "member_count",
            "created_at",
            "updated_at",
        ]

        # Read-only fields
        read_only_fields = [
            "id",
            "owner",
            "created_at",
            "updated_at",
        ]
