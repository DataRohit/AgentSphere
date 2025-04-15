# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
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


# MCPServer list me response serializer
class MCPServerListMeResponseSerializer(GenericResponseSerializer):
    """MCPServer list me response serializer.

    This serializer defines the structure of the response for the 'mcpserver/list/me' endpoint.
    It includes a status code and a list of MCP servers created by the current user.

    Attributes:
        status_code (int): The status code of the response.
        mcpservers (List[MCPServerSerializer]): List of MCP server objects created by the current user.
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
            "List of MCP servers created by the current user with detailed information.",
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


# Missing required parameter error response serializer
class MCPServerListMissingParamResponseSerializer(GenericResponseSerializer):
    """Missing required parameter error response serializer.

    This serializer defines the structure of the 400 Bad Request error response
    when a required parameter is missing from the request.

    Attributes:
        status_code (int): The status code of the response (400 Bad Request).
        error (str): An error message explaining the missing parameter.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("Missing required parameter: organization_id"),
        read_only=True,
        help_text=_("Error message explaining the missing parameter."),
    )
