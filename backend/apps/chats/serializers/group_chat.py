# Third-party imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

# Local application imports
from apps.chats.models import GroupChat


# GroupChat organization nested serializer for API documentation
class GroupChatOrganizationSerializer(serializers.Serializer):
    """GroupChat organization serializer for use in group chat responses.

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


# GroupChat user nested serializer for API documentation
class GroupChatUserSerializer(serializers.Serializer):
    """GroupChat user serializer for use in group chat responses.

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


# GroupChat agent nested serializer for API documentation
class GroupChatAgentSerializer(serializers.Serializer):
    """GroupChat agent serializer for use in group chat responses.

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


# GroupChat serializer
class GroupChatSerializer(serializers.ModelSerializer):
    """Serializer for the GroupChat model.

    This serializer provides a representation of a group chat between
    a user and multiple agents, including details about the organization, user, and agents.

    Attributes:
        id (UUID): The chat's ID.
        title (str): The chat's title.
        is_public (bool): Whether this chat is publicly visible to other users in the organization.
        organization (dict): Organization details including id and name.
        user (dict): User details including id and username.
        agents (list): List of agent details including id and name.
        summary (TextField): A summary of the chat conversation.
        created_at (datetime): The date and time the chat was created.
        updated_at (datetime): The date and time the chat was last updated.

    Meta:
        model (GroupChat): The GroupChat model.
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

    # Agents details
    agents = serializers.SerializerMethodField(
        help_text=_("Agents details who participate in the chat."),
    )

    # Meta class for GroupChatSerializer configuration
    class Meta:
        """Meta class for GroupChatSerializer configuration.

        Attributes:
            model (GroupChat): The model class.
            fields (list): The fields to include in the serializer.
            read_only_fields (list): Fields that are read-only.
        """

        # Model to use for the serializer
        model = GroupChat

        # Fields to include in the serializer
        fields = [
            "id",
            "title",
            "is_public",
            "organization",
            "user",
            "agents",
            "summary",
            "created_at",
            "updated_at",
        ]

        # Read-only fields
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "summary",
        ]

    # Get organization details
    @extend_schema_field(GroupChatOrganizationSerializer())
    def get_organization(self, obj: GroupChat) -> dict | None:
        """Get organization details for the chat.

        Args:
            obj (GroupChat): The group chat instance.

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
    @extend_schema_field(GroupChatUserSerializer())
    def get_user(self, obj: GroupChat) -> dict | None:
        """Get user details for the chat.

        Args:
            obj (GroupChat): The group chat instance.

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

    # Get agents details
    @extend_schema_field(serializers.ListField(child=GroupChatAgentSerializer()))
    def get_agents(self, obj: GroupChat) -> list:
        """Get agents details for the chat.

        Args:
            obj (GroupChat): The group chat instance.

        Returns:
            list: The agents details including id and name.
        """

        # If the chat has agents
        if obj.agents.exists():
            # Return the agents details with string UUID
            return [
                {
                    "id": str(agent.id),
                    "name": agent.name,
                }
                for agent in obj.agents.all()
            ]

        # Return empty list if the chat has no agents
        return []


# GroupChat response schema for Swagger documentation
class GroupChatResponseSchema(serializers.Serializer):
    """GroupChat response schema for Swagger documentation.

    Defines the structure of a group chat in the response.

    Attributes:
        id (UUID): The chat's ID.
        title (str): The chat's title.
        is_public (bool): Whether this chat is publicly visible to other users in the organization.
        organization (SingleChatOrganizationSerializer): Organization details including id and name.
        user (SingleChatUserSerializer): User details including id, username, and email.
        agents (list): List of agent details including id and name.
        summary (TextField): A summary of the chat conversation.
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

    # Summary field
    summary = serializers.CharField(
        help_text=_("A summary of the chat conversation."),
        allow_blank=True,
    )

    # Organization field using the proper serializer
    organization = GroupChatOrganizationSerializer(
        help_text=_("Organization details the chat belongs to."),
        required=False,
        allow_null=True,
    )

    # User field using the proper serializer
    user = GroupChatUserSerializer(
        help_text=_("User details who participates in the chat."),
        required=False,
        allow_null=True,
    )

    # Agents field using a list of agent serializers
    agents = serializers.ListField(
        child=GroupChatAgentSerializer(),
        help_text=_("Agents details who participate in the chat."),
        required=False,
    )
