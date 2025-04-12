# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Project imports
from apps.common.serializers import GenericResponseSerializer


# MCPServer delete success response serializer
class MCPServerDeleteSuccessResponseSerializer(GenericResponseSerializer):
    """MCPServer delete success response serializer.

    This serializer defines the structure of the MCP server delete success response.
    It includes a status code and a success message.

    Attributes:
        status_code (int): The status code of the response.
        message (str): A success message.
    """

    # MCPServer delete success message response serializer
    class MCPServerDeleteSuccessMessageResponseSerializer(serializers.Serializer):
        """MCPServer delete success message response serializer.

        Attributes:
            message (str): A success message.
        """

        # Message
        message = serializers.CharField(
            default=_("MCP server deleted successfully."),
            read_only=True,
            help_text=_("Success message confirming the MCP server was deleted."),
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Success message
    mcpserver = MCPServerDeleteSuccessMessageResponseSerializer(
        read_only=True,
        help_text=_("Success message confirming the MCP server was deleted."),
    )


# Permission denied error response serializer for delete
class MCPServerDeletePermissionDeniedResponseSerializer(GenericResponseSerializer):
    """Permission denied error response serializer for delete operation.

    This serializer defines the structure of the permission denied error response
    when attempting to delete an MCP server.

    Attributes:
        status_code (int): The status code of the response (403 Forbidden).
        error (str): An error message explaining the permission denial.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_403_FORBIDDEN,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("You do not have permission to delete this MCP server."),
        read_only=True,
        help_text=_("Error message explaining the permission denial."),
    )


# MCPServer not found error response serializer for delete
class MCPServerDeleteNotFoundResponseSerializer(GenericResponseSerializer):
    """MCPServer not found error response serializer for delete operation.

    This serializer defines the structure of the 404 Not Found error response
    when the specified MCP server to delete cannot be found.

    Attributes:
        status_code (int): The status code of the response (404 Not Found).
        error (str): An error message explaining why the MCP server wasn't found.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_404_NOT_FOUND,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("MCP server not found."),
        read_only=True,
        help_text=_("Error message explaining why the MCP server wasn't found."),
    )
