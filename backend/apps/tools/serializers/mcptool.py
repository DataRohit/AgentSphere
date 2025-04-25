# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

# Local application imports
from apps.tools.models import MCPTool


# MCPTool serializer
class MCPToolSerializer(serializers.ModelSerializer):
    """MCPTool serializer.

    This serializer provides a representation of the MCPTool model
    with only the name and description fields.

    Attributes:
        id (UUID): The tool's ID.
        name (str): The tool's name.
        description (str): The tool's description.
    """

    # ID field
    id = serializers.UUIDField(
        help_text=_("Unique identifier for the MCP tool."),
        read_only=True,
    )

    # Name field
    name = serializers.CharField(
        help_text=_("Name of the MCP tool."),
    )

    # Description field
    description = serializers.CharField(
        help_text=_("Description of the MCP tool."),
        allow_blank=True,
    )

    # Meta class for MCPToolSerializer configuration
    class Meta:
        """Meta class for MCPToolSerializer configuration.

        Attributes:
            model (MCPTool): The model class.
            fields (list): The fields to include in the serializer.
            read_only_fields (list): Fields that are read-only.
        """

        # Model to use for the serializer
        model = MCPTool

        # Fields to include in the serializer
        fields = [
            "id",
            "name",
            "description",
        ]

        # Read-only fields
        read_only_fields = [
            "id",
        ]
