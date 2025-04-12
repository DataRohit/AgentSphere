# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Project imports
from apps.common.serializers import GenericResponseSerializer
from apps.tools.serializers.mcpserver import MCPServerSerializer


# MCPServer detail success response serializer
class MCPServerDetailSuccessResponseSerializer(GenericResponseSerializer):
    """MCPServer detail success response serializer.

    This serializer defines the structure of the MCPServer detail success response.
    It includes a status code and an MCPServer object.

    Attributes:
        status_code (int): The status code of the response.
        mcpserver (MCPServerSerializer): The MCPServer details with organization and user information.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # MCPServer data
    mcpserver = MCPServerSerializer(
        help_text=_("The MCPServer details with organization and user information."),
        read_only=True,
    )


# MCPServer detail not found response serializer
class MCPServerDetailNotFoundResponseSerializer(GenericResponseSerializer):
    """MCPServer detail not found response serializer.

    This serializer defines the structure of the MCPServer detail not found response.
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
        default="MCP server not found.",
        read_only=True,
        help_text=_("Error message."),
    )


# MCPServer detail permission denied response serializer
class MCPServerDetailPermissionDeniedResponseSerializer(GenericResponseSerializer):
    """MCPServer detail permission denied response serializer.

    This serializer defines the structure of the MCPServer detail permission denied response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response.
        error (str): An error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_403_FORBIDDEN,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default="You do not have permission to view this MCP server.",
        read_only=True,
        help_text=_("Error message."),
    )
