# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Project imports
from apps.common.serializers import GenericResponseSerializer
from apps.tools.serializers.mcpserver import MCPServerSerializer


# MCPServer list response serializer
class MCPServerListResponseSerializer(GenericResponseSerializer):
    """MCPServer list response serializer.

    This serializer defines the structure of the MCPServer list response.
    It includes a status code and a list of MCP servers.

    Attributes:
        status_code (int): The status code of the response.
        mcpservers (List[MCPServerSerializer]): List of MCP server objects with detailed information.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # MCPServer list
    mcpservers = MCPServerSerializer(
        many=True,
        read_only=True,
        help_text=_(
            "List of MCP servers with detailed information about organization and user.",
        ),
    )


# MCPServer list not found response serializer
class MCPServerListNotFoundResponseSerializer(GenericResponseSerializer):
    """MCPServer list not found response serializer.

    This serializer defines the structure of the MCPServer list not found response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response.
        error (str): An error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_404_NOT_FOUND,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default="No MCP servers found matching the criteria.",
        read_only=True,
        help_text=_("Error message."),
    )
