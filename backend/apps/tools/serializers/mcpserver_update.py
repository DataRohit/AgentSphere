# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer
from apps.tools.models import MCPServer
from apps.tools.serializers.mcpserver import MCPServerSerializer


# MCPServer update serializer
class MCPServerUpdateSerializer(serializers.ModelSerializer):
    """MCPServer update serializer.

    This serializer handles updating existing MCP servers. It validates
    that the MCP server exists and the user has permission to update it.

    Attributes:
        name (CharField): The name of the MCP server.
        description (TextField): A description of the MCP server.
        url (URLField): The URL of the MCP server.
        tags (CharField): Optional tags for categorizing the server.

    Meta:
        model (MCPServer): The MCPServer model.
        fields (list): The fields to include in the serializer.

    Returns:
        MCPServer: The updated MCPServer instance.
    """

    # Meta class for MCPServerUpdateSerializer configuration
    class Meta:
        """Meta class for MCPServerUpdateSerializer configuration.

        Attributes:
            model (MCPServer): The model class.
            fields (list): The fields to include in the serializer.
            extra_kwargs (dict): Additional field configurations.
        """

        # Model to use for the serializer
        model = MCPServer

        # Fields to include in the serializer
        fields = [
            "name",
            "description",
            "url",
            "tags",
        ]

        # Extra kwargs
        extra_kwargs = {
            "name": {"required": False},
            "description": {"required": False},
            "url": {"required": False, "help_text": _("URL of the MCP server. Must be unique.")},
            "tags": {"required": False},
        }


# MCPServer update success response serializer
class MCPServerUpdateSuccessResponseSerializer(GenericResponseSerializer):
    """MCPServer update success response serializer.

    This serializer defines the structure of the MCP server update success response.
    It includes a status code and an MCP server object.

    Attributes:
        status_code (int): The status code of the response.
        mcpserver (MCPServerSerializer): The updated MCP server with detailed organization and user information.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # MCPServer data
    mcpserver = MCPServerSerializer(
        help_text=_(
            "The updated MCP server with detailed organization and user information.",
        ),
        read_only=True,
    )


# MCPServer update error response serializer
class MCPServerUpdateErrorResponseSerializer(GenericResponseSerializer):
    """MCPServer update error response serializer (for schema).

    This serializer defines the structure of the wrapped validation error response
    as it would be formatted for documentation purposes.

    Attributes:
        status_code (int): The status code of the response.
        errors (MCPServerUpdateErrorsDetailSerializer): The errors detail serializer.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Nested serializer defining the structure of the actual errors
    class MCPServerUpdateErrorsDetailSerializer(serializers.Serializer):
        """MCPServer Update Errors detail serializer.

        Attributes:
            name (list): Errors related to the name field.
            description (list): Errors related to the description field.
            url (list): Errors related to the URL field.
            tags (list): Errors related to the tags field.
            non_field_errors (list): Non-field specific errors.
        """

        # Name field
        name = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the name field."),
        )

        # Description field
        description = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the description field."),
        )

        # URL field
        url = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the URL field, including uniqueness violations."),
        )

        # Tags field
        tags = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the tags field."),
        )

        # Non-field errors
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Non-field specific errors."),
        )

    # Define the 'errors' field containing the validation error details
    errors = MCPServerUpdateErrorsDetailSerializer(
        help_text=_("Validation errors for the MCP server update request."),
        read_only=True,
    )


# MCPServer not found response serializer
class MCPServerNotFoundResponseSerializer(GenericResponseSerializer):
    """MCPServer not found response serializer.

    This serializer defines the structure of the MCP server not found response.
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


# MCPServer permission denied response serializer
class MCPServerPermissionDeniedResponseSerializer(GenericResponseSerializer):
    """MCPServer permission denied response serializer.

    This serializer defines the structure of the MCP server permission denied response.
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
        default="You do not have permission to update this MCP server.",
        read_only=True,
        help_text=_("Error message."),
    )
