# Third-party imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

# Local application imports
from apps.chats.models import SingleChat


# SingleChat organization nested serializer for API documentation
class SingleChatOrganizationSerializer(serializers.Serializer):
    """SingleChat organization serializer for use in single chat responses.

    Attributes:
        id (UUID): Organization's unique identifier.
        name (str): Name of the organization.
    """

    # ID field
    id = serializers.UUIDField(
        help_text=_("Unique identifier for the organization."),
        read_only=True,
    )

    # Name field
    name = serializers.CharField(
        help_text=_("Name of the organization."),
        read_only=True,
    )


# SingleChat user nested serializer for API documentation
class SingleChatUserSerializer(serializers.Serializer):
    """SingleChat user serializer for use in single chat responses.

    Attributes:
        id (UUID): User's unique identifier.
        username (str): Username of the user.
        email (str): Email of the user.
    """

    # ID field
    id = serializers.UUIDField(
        help_text=_("Unique identifier for the user."),
        read_only=True,
    )

    # Username field
    username = serializers.CharField(
        help_text=_("Username of the user."),
        read_only=True,
    )

    # Email field
    email = serializers.EmailField(
        help_text=_("Email of the user."),
        read_only=True,
    )


# SingleChat agent nested serializer for API documentation
class SingleChatAgentSerializer(serializers.Serializer):
    """SingleChat agent serializer for use in single chat responses.

    Attributes:
        id (UUID): Agent's unique identifier.
        name (str): Name of the agent.
    """

    # ID field
    id = serializers.UUIDField(
        help_text=_("Unique identifier for the agent."),
        read_only=True,
    )

    # Name field
    name = serializers.CharField(
        help_text=_("Name of the agent."),
        read_only=True,
    )


# SingleChat serializer
class SingleChatSerializer(serializers.ModelSerializer):
    """Serializer for the SingleChat model.

    This serializer provides a representation of a single chat between
    a user and an agent, including details about the organization, user, and agent.

    Attributes:
        id (UUID): The chat's ID.
        title (str): The chat's title.
        is_public (bool): Whether this chat is publicly visible to other users in the organization.
        organization (dict): Organization details including id and name.
        user (dict): User details including id and username.
        agent (dict): Agent details including id and name.
        created_at (datetime): The date and time the chat was created.
        updated_at (datetime): The date and time the chat was last updated.

    Meta:
        model (SingleChat): The SingleChat model.
        fields (list): The fields to include in the serializer.
        read_only_fields (list): Fields that are read-only.
    """

    # Organization details
    organization = serializers.SerializerMethodField(
        help_text=_("Organization details the chat belongs to."),
    )

    # User details
    user = serializers.SerializerMethodField(
        help_text=_("User details who participates in the chat."),
    )

    # Agent details
    agent = serializers.SerializerMethodField(
        help_text=_("Agent details who participates in the chat."),
    )

    # Meta class for SingleChatSerializer configuration
    class Meta:
        """Meta class for SingleChatSerializer configuration.

        Attributes:
            model (SingleChat): The model class.
            fields (list): The fields to include in the serializer.
            read_only_fields (list): Fields that are read-only.
        """

        # Model to use for the serializer
        model = SingleChat

        # Fields to include in the serializer
        fields = [
            "id",
            "title",
            "is_public",
            "organization",
            "user",
            "agent",
            "created_at",
            "updated_at",
        ]

        # Read-only fields
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    # Get organization details
    @extend_schema_field(SingleChatOrganizationSerializer())
    def get_organization(self, obj: SingleChat) -> dict | None:
        """Get organization details for the chat.

        Args:
            obj (SingleChat): The single chat instance.

        Returns:
            dict | None: The organization details including id and name.
        """

        # If the chat has an organization
        if obj.organization:
            # Return the organization details with string UUID
            return {
                "id": str(obj.organization.id),
                "name": obj.organization.name,
            }

        # Return None if the chat has no organization
        return None

    # Get user details
    @extend_schema_field(SingleChatUserSerializer())
    def get_user(self, obj: SingleChat) -> dict | None:
        """Get user details for the chat.

        Args:
            obj (SingleChat): The single chat instance.

        Returns:
            dict | None: The user details including id, username, and email.
        """

        # If the chat has a user
        if obj.user:
            # Return the user details with string UUID
            return {
                "id": str(obj.user.id),
                "username": obj.user.username,
                "email": obj.user.email,
            }

        # Return None if the chat has no user
        return None

    # Get agent details
    @extend_schema_field(SingleChatAgentSerializer())
    def get_agent(self, obj: SingleChat) -> dict | None:
        """Get agent details for the chat.

        Args:
            obj (SingleChat): The single chat instance.

        Returns:
            dict | None: The agent details including id and name.
        """

        # If the chat has an agent
        if obj.agent:
            # Return the agent details with string UUID
            return {
                "id": str(obj.agent.id),
                "name": obj.agent.name,
            }

        # Return None if the chat has no agent
        return None


# SingleChat response schema for Swagger documentation
class SingleChatResponseSchema(serializers.Serializer):
    """SingleChat response schema for Swagger documentation.

    Defines the structure of a single chat in the response.

    Attributes:
        id (UUID): The chat's ID.
        title (str): The chat's title.
        is_public (bool): Whether this chat is publicly visible to other users in the organization.
        organization (SingleChatOrganizationSerializer): Organization details including id and name.
        user (SingleChatUserSerializer): User details including id, username, and email.
        agent (SingleChatAgentSerializer): Agent details including id and name.
        created_at (datetime): The date and time the chat was created.
        updated_at (datetime): The date and time the chat was last updated.
    """

    # ID field
    id = serializers.UUIDField(
        help_text=_("Unique identifier for the chat."),
    )

    # Title field
    title = serializers.CharField(
        help_text=_("Title of the chat."),
    )

    # Is public field
    is_public = serializers.BooleanField(
        help_text=_("Whether this chat is publicly visible to other users in the organization."),
    )

    # Created at field
    created_at = serializers.DateTimeField(
        help_text=_("Timestamp when the chat was created."),
    )

    # Updated at field
    updated_at = serializers.DateTimeField(
        help_text=_("Timestamp when the chat was last updated."),
    )

    # Organization field using the proper serializer
    organization = SingleChatOrganizationSerializer(
        help_text=_("Organization details the chat belongs to."),
        required=False,
        allow_null=True,
    )

    # User field using the proper serializer
    user = SingleChatUserSerializer(
        help_text=_("User details who participates in the chat."),
        required=False,
        allow_null=True,
    )

    # Agent field using the proper serializer
    agent = SingleChatAgentSerializer(
        help_text=_("Agent details who participates in the chat."),
        required=False,
        allow_null=True,
    )
