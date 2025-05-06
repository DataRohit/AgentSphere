# Third-party imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

# Local application imports
from apps.llms.models import LLM


# LLM organization nested serializer for API documentation
class LLMOrganizationSerializer(serializers.Serializer):
    """LLM organization serializer for use in LLM responses.

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


# LLM user nested serializer for API documentation
class LLMUserSerializer(serializers.Serializer):
    """LLM user serializer for use in LLM responses.

    Attributes:
        id (UUID): User's unique identifier.
        username (str): Username of the user.
        email (str): Email address of the user.
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
        help_text=_("Email address of the user."),
        read_only=True,
    )


# LLM serializer
class LLMSerializer(serializers.ModelSerializer):
    """LLM serializer.

    This serializer provides a representation of the LLM model.

    Attributes:
        id (UUID): The LLM's ID.
        base_url (str): The base URL for the LLM API.
        model (str): The specific model name.
        max_tokens (int): Maximum tokens for generation.
        organization (dict): Organization details including id and name.
        user (dict): User details including id, username, and email.
        created_at (datetime): The date and time the LLM was created.
        updated_at (datetime): The date and time the LLM was last updated.

    Meta:
        model (LLM): The model class.
        fields (list): The fields to include in the serializer.
        read_only_fields (list): Fields that are read-only.
    """

    # Organization details
    organization = serializers.SerializerMethodField(
        help_text=_("Organization details the LLM belongs to."),
    )

    # User details
    user = serializers.SerializerMethodField(
        help_text=_("User details who created the LLM."),
    )

    # Meta class for LLMSerializer configuration
    class Meta:
        """Meta class for LLMSerializer configuration.

        Attributes:
            model (LLM): The model class.
            fields (list): The fields to include in the serializer.
            read_only_fields (list): Fields that are read-only.
        """

        # Model to use for the serializer
        model = LLM

        # Fields to include in the serializer
        fields = [
            "id",
            "base_url",
            "model",
            "max_tokens",
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

    # Get organization details
    @extend_schema_field(LLMOrganizationSerializer())
    def get_organization(self, obj: LLM) -> dict:
        """Get organization details for the LLM.

        Args:
            obj (LLM): The LLM instance.

        Returns:
            dict: The organization details including id and name.
        """

        # If the LLM has an organization
        if obj.organization:
            # Return the organization details with string UUID
            return {
                "id": str(obj.organization.id),
                "name": obj.organization.name,
            }

        # If the LLM does not have an organization, return None
        return None

    # Get user details
    @extend_schema_field(LLMUserSerializer())
    def get_user(self, obj: LLM) -> dict:
        """Get user details for the LLM.

        Args:
            obj (LLM): The LLM instance.

        Returns:
            dict: The user details including id, username, and email.
        """

        # If the LLM has a user
        if obj.user:
            # Return the user details with string UUID
            return {
                "id": str(obj.user.id),
                "username": obj.user.username,
                "email": obj.user.email,
            }

        # If the LLM does not have a user, return None
        return None

    # Convert the LLM instance to its serialized representation
    def to_representation(self, instance: LLM) -> dict:
        """Convert the LLM instance to its serialized representation.

        Args:
            instance (LLM): The LLM instance.

        Returns:
            dict: The serialized representation.
        """

        # Get the standard representation and return it
        return super().to_representation(instance)


# Define explicit LLM response schema for Swagger documentation
class LLMResponseSchema(serializers.Serializer):
    """LLM response schema for Swagger documentation.

    Defines the structure of an LLM in the response.

    Attributes:
        id (UUID): The LLM's ID.
        base_url (str): The base URL for the LLM API.
        model (str): The specific model name.
        max_tokens (int): Maximum tokens for generation.
        organization (LLMOrganizationSerializer): Organization details including id and name.
        user (LLMUserSerializer): User details including id, username, and email.
        created_at (datetime): The date and time the LLM was created.
        updated_at (datetime): The date and time the LLM was last updated.
    """

    # ID field
    id = serializers.UUIDField(
        help_text=_("Unique identifier for the LLM."),
    )

    # Base URL field
    base_url = serializers.URLField(
        help_text=_("Base URL for the LLM API."),
    )

    # Model field
    model = serializers.CharField(
        help_text=_("Specific model name to use with this LLM API."),
    )

    # Max tokens field
    max_tokens = serializers.IntegerField(
        help_text=_("Maximum number of tokens for generation."),
    )

    # Created at field
    created_at = serializers.DateTimeField(
        help_text=_("Timestamp when the LLM was created."),
    )

    # Updated at field
    updated_at = serializers.DateTimeField(
        help_text=_("Timestamp when the LLM was last updated."),
    )

    # Organization field using the proper serializer
    organization = LLMOrganizationSerializer(
        help_text=_("Organization details the LLM belongs to."),
        required=False,
        allow_null=True,
    )

    # User field using the proper serializer
    user = LLMUserSerializer(
        help_text=_("User details who created the LLM."),
        required=False,
        allow_null=True,
    )
