# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

# Project imports
from apps.agents.models import LLM


# LLM serializer
class LLMSerializer(serializers.ModelSerializer):
    """LLM serializer.

    This serializer provides a representation of the LLM model.

    Attributes:
        id (UUID): The LLM's ID.
        api_type (str): The API provider type (Ollama or Gemini).
        model (str): The specific model name.
        max_tokens (int): Maximum tokens for generation.
        organization_id (UUID): The ID of the organization the LLM belongs to.
        user_id (UUID): The ID of the user who created the LLM.
        created_at (datetime): The date and time the LLM was created.
        updated_at (datetime): The date and time the LLM was last updated.

    Meta:
        model (LLM): The model class.
        fields (list): The fields to include in the serializer.
        read_only_fields (list): Fields that are read-only.
    """

    # Organization ID field
    organization_id = serializers.UUIDField(
        source="organization.id",
        read_only=True,
        help_text=_("ID of the organization the LLM belongs to."),
    )

    # User ID field
    user_id = serializers.UUIDField(
        source="user.id",
        read_only=True,
        help_text=_("ID of the user who created the LLM."),
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
            "api_type",
            "model",
            "max_tokens",
            "organization_id",
            "user_id",
            "created_at",
            "updated_at",
        ]

        # Read-only fields
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    # Convert the LLM instance to its serialized representation
    def to_representation(self, instance: LLM) -> dict:
        """Convert the LLM instance to its serialized representation.

        Override to handle the API type display name.

        Args:
            instance (LLM): The LLM instance.

        Returns:
            dict: The serialized representation.
        """

        # Get the standard representation
        representation = super().to_representation(instance)

        # Add the API type display name
        representation["api_type_display"] = instance.get_api_type_display()

        # Return the representation
        return representation


# Define explicit LLM response schema for Swagger documentation
class LLMResponseSchema(serializers.Serializer):
    """LLM response schema for Swagger documentation.

    Defines the structure of an LLM in the response.

    Attributes:
        id (UUID): The LLM's ID.
        api_type (str): The API provider type (Ollama or Gemini).
        api_type_display (str): The human-readable display name for the API type.
        model (str): The specific model name.
        max_tokens (int): Maximum tokens for generation.
        organization_id (UUID): The ID of the organization the LLM belongs to.
        user_id (UUID): The ID of the user who created the LLM.
        created_at (datetime): The date and time the LLM was created.
        updated_at (datetime): The date and time the LLM was last updated.
    """

    # ID field
    id = serializers.UUIDField(
        help_text=_("Unique identifier for the LLM."),
    )

    # API type field
    api_type = serializers.CharField(
        help_text=_("API provider type code (ollama or gemini)."),
    )

    # API type display field
    api_type_display = serializers.CharField(
        help_text=_("Human-readable display name for the API type."),
    )

    # Model field
    model = serializers.CharField(
        help_text=_("Specific model name for the selected API type."),
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

    # Organization ID field
    organization_id = serializers.UUIDField(
        help_text=_("ID of the organization the LLM belongs to."),
        source="organization.id",
    )

    # User ID field
    user_id = serializers.UUIDField(
        help_text=_("ID of the user who created the LLM."),
        source="user.id",
    )
