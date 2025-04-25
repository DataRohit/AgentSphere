# Third-party imports
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.organization.models import Organization

# Local application imports
from apps.tools.models import MCPServer

# Get the User model
User = get_user_model()


# Organization serializer for MCPServer
class MCPServerOrganizationSerializer(serializers.ModelSerializer):
    """Organization serializer for MCPServer.

    This serializer provides a representation of the Organization model
    for use in the MCPServer serializer.

    Attributes:
        id (UUID): The organization's ID.
        name (str): The organization's name.
    """

    # ID field
    id = serializers.UUIDField(
        help_text=_("Unique identifier for the organization."),
    )

    # Name field
    name = serializers.CharField(
        help_text=_("Name of the organization."),
    )

    # Meta class for MCPServerOrganizationSerializer configuration
    class Meta:
        """Meta class for MCPServerOrganizationSerializer configuration.

        Attributes:
            model (Organization): The model class.
            fields (list): The fields to include in the serializer.
        """

        # Model to use for the serializer
        model = Organization

        # Fields to include in the serializer
        fields = [
            "id",
            "name",
        ]


# User serializer for MCPServer
class MCPServerUserSerializer(serializers.ModelSerializer):
    """User serializer for MCPServer.

    This serializer provides a representation of the User model
    for use in the MCPServer serializer.

    Attributes:
        id (UUID): The user's ID.
        username (str): The user's username.
        email (str): The user's email address.
    """

    # ID field
    id = serializers.UUIDField(
        help_text=_("Unique identifier for the user."),
    )

    # Username field
    username = serializers.CharField(
        help_text=_("Username of the user."),
    )

    # Email field
    email = serializers.EmailField(
        help_text=_("Email address of the user."),
    )

    # Meta class for MCPServerUserSerializer configuration
    class Meta:
        """Meta class for MCPServerUserSerializer configuration.

        Attributes:
            model (User): The model class.
            fields (list): The fields to include in the serializer.
        """

        # Model to use for the serializer
        model = User

        # Fields to include in the serializer
        fields = [
            "id",
            "username",
            "email",
        ]


# MCPServer serializer
class MCPServerSerializer(serializers.ModelSerializer):
    """MCPServer serializer.

    This serializer provides a representation of the MCPServer model.

    Attributes:
        id (UUID): The server's ID.
        name (str): The server's name.
        description (str): The server's description.
        url (str): The server's URL.
        tags (str): Comma-separated tags for categorizing the server.
        organization (dict): Organization details including id and name.
        user (dict): User details including id, username, and email.
        created_at (datetime): The date and time the server was created.
        updated_at (datetime): The date and time the server was last updated.

    Meta:
        model (MCPServer): The model class.
        fields (list): The fields to include in the serializer.
        read_only_fields (list): Fields that are read-only.
    """

    # ID field
    id = serializers.UUIDField(
        help_text=_("Unique identifier for the MCP server."),
    )

    # Name field
    name = serializers.CharField(
        help_text=_("Name of the MCP server."),
    )

    # Description field
    description = serializers.CharField(
        help_text=_("Description of the MCP server."),
        allow_blank=True,
    )

    # URL field
    url = serializers.URLField(
        help_text=_("URL of the MCP server. Must be unique."),
    )

    # Tags field
    tags = serializers.CharField(
        help_text=_("Comma-separated tags for categorizing the server."),
        allow_blank=True,
    )

    # Organization field - nested serializer
    organization = MCPServerOrganizationSerializer(
        read_only=True,
        help_text=_("Organization details including id and name."),
    )

    # User field - nested serializer
    user = MCPServerUserSerializer(
        read_only=True,
        help_text=_("User details including id, username, and email."),
    )

    # Created at field
    created_at = serializers.DateTimeField(
        help_text=_("Date and time when the MCP server was created."),
    )

    # Updated at field
    updated_at = serializers.DateTimeField(
        help_text=_("Date and time when the MCP server was last updated."),
    )

    # Meta class for MCPServerSerializer configuration
    class Meta:
        """Meta class for MCPServerSerializer configuration.

        Attributes:
            model (MCPServer): The model class.
            fields (list): The fields to include in the serializer.
            read_only_fields (list): Fields that are read-only.
        """

        # Model to use for the serializer
        model = MCPServer

        # Fields to include in the serializer
        fields = [
            "id",
            "name",
            "description",
            "url",
            "tags",
            "organization",
            "user",
            "created_at",
            "updated_at",
        ]

        # Read-only fields
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
