# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer
from apps.organization.models import Organization
from apps.tools.models import MCPServer
from apps.tools.serializers.mcpserver import MCPServerSerializer


# MCPServer creation serializer
class MCPServerCreateSerializer(serializers.ModelSerializer):
    """MCPServer creation serializer.

    This serializer handles the creation of new MCP servers. It validates that
    the user is a member of the specified organization and has not exceeded
    the maximum number of MCP servers they can create per organization.
    The organization_id is provided in the request body.

    Attributes:
        organization_id (UUIDField): The ID of the organization to create the server in.
        name (CharField): The name of the server.
        tool_name (CharField): The name of the tool provided by this MCP server.
        description (TextField): A description of the server.
        url (URLField): The URL of the server.
        tags (CharField): Optional tags for categorizing the server.

    Meta:
        model (MCPServer): The MCPServer model.
        fields (list): The fields to include in the serializer.
        extra_kwargs (dict): Additional field configurations.

    Raises:
        serializers.ValidationError: If user is not a member of the organization.
        serializers.ValidationError: If user has exceeded the maximum number of MCP servers per organization.

    Returns:
        MCPServer: The newly created MCP server instance.
    """

    # Organization ID field
    organization_id = serializers.UUIDField(
        help_text=_("The ID of the organization to create the server in."),
        required=True,
    )

    # Meta class for MCPServerCreateSerializer configuration
    class Meta:
        """Meta class for MCPServerCreateSerializer configuration.

        Attributes:
            model (MCPServer): The model class.
            fields (list): The fields to include in the serializer.
            extra_kwargs (dict): Additional field configurations.
        """

        # Model to use for the serializer
        model = MCPServer

        # Fields to include in the serializer
        fields = [
            "organization_id",
            "name",
            "tool_name",
            "description",
            "url",
            "tags",
        ]

        # Extra kwargs
        extra_kwargs = {
            "name": {"required": True},
            "tool_name": {"required": False},
            "description": {"required": False},
            "url": {"required": True},
            "tags": {"required": False},
        }

    # Validate the serializer data
    def validate(self, attrs: dict) -> dict:
        """Validate the serializer data.

        This method validates that:
        1. The user is a member of the specified organization.
        2. The user has not exceeded the maximum number of MCP servers they can create per organization.

        Args:
            attrs (dict): The attributes to validate.

        Returns:
            dict: The validated attributes.

        Raises:
            serializers.ValidationError: If validation fails.
        """

        # Get the user from the context
        user = self.context["request"].user

        # Get the organization ID from the request data
        organization_id = attrs.pop("organization_id")

        try:
            # Try to get the organization
            organization = Organization.objects.get(id=organization_id)

            # Check if the user is the owner or a member of the organization
            if user != organization.owner and user not in organization.members.all():
                # Raise a validation error
                raise serializers.ValidationError(
                    {
                        "non_field_errors": [
                            _("You are not a member of this organization."),
                        ],
                    },
                )

            # Count the number of MCP servers the user has created in this organization
            user_mcpserver_count = MCPServer.objects.filter(
                user=user,
                organization=organization,
            ).count()

            # Check if the user has reached the maximum number of MCP servers per organization
            if user_mcpserver_count >= MCPServer.MAX_MCPSERVERS_PER_USER_PER_ORGANIZATION:
                # Set the error message
                error_message = f"You can only create a maximum of {MCPServer.MAX_MCPSERVERS_PER_USER_PER_ORGANIZATION} MCP servers per organization."  # noqa: E501

                # Raise a validation error
                raise serializers.ValidationError(
                    {
                        "non_field_errors": [
                            _(
                                error_message,
                            ).format(
                                MCPServer.MAX_MCPSERVERS_PER_USER_PER_ORGANIZATION,
                            ),
                        ],
                    },
                )

            # Store the organization in attrs for later use
            attrs["organization"] = organization

            # Store the user in attrs for later use
            attrs["user"] = user

        except Organization.DoesNotExist:
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        _("Organization not found."),
                    ],
                },
            ) from None

        # Return the validated data
        return attrs

    # Create method to create a new MCP server
    def create(self, validated_data: dict) -> MCPServer:
        """Create a new MCP server with the validated data.

        Args:
            validated_data (dict): The validated data.

        Returns:
            MCPServer: The newly created MCP server.
        """

        # Create and return a new MCP server with the validated data
        return MCPServer.objects.create(**validated_data)


# MCPServer creation success response serializer
class MCPServerCreateSuccessResponseSerializer(GenericResponseSerializer):
    """MCPServer creation success response serializer.

    This serializer defines the structure of the MCP server creation success response.
    It includes a status code and an MCP server object.

    Attributes:
        status_code (int): The status code of the response.
        mcpserver (MCPServerSerializer): The newly created MCP server with detailed organization and user information.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_201_CREATED,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # MCPServer data
    mcpserver = MCPServerSerializer(
        help_text=_(
            "The newly created MCP server with detailed organization and user information.",
        ),
    )


# MCPServer creation error response serializer
class MCPServerCreateErrorResponseSerializer(GenericResponseSerializer):
    """MCPServer creation error response serializer (for schema).

    This serializer defines the structure of the wrapped validation error response
    as it would be formatted for documentation purposes.

    Attributes:
        status_code (int): The status code of the response.
        errors (MCPServerCreateErrorsDetailSerializer): The errors detail serializer.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Nested serializer defining the structure of the actual errors
    class MCPServerCreateErrorsDetailSerializer(serializers.Serializer):
        """MCPServer Creation Errors detail serializer.

        Attributes:
            organization_id (list): Errors related to the organization_id field.
            name (list): Errors related to the name field.
            url (list): Errors related to the URL field.
            non_field_errors (list): Non-field specific errors.
        """

        # Organization ID field
        organization_id = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the organization_id field."),
        )

        # Name field
        name = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the name field."),
        )

        # URL field
        url = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the URL field."),
        )

        # Non-field errors
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Non-field specific errors."),
        )

    # Errors field
    errors = MCPServerCreateErrorsDetailSerializer(
        help_text=_("Validation errors for the MCP server creation request."),
    )


# MCPServer authentication error response serializer
class MCPServerAuthErrorResponseSerializer(GenericResponseSerializer):
    """MCPServer authentication error response serializer.

    This serializer defines the structure of the authentication error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response.
        error (str): The error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_401_UNAUTHORIZED,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("Authentication credentials were not provided."),
        read_only=True,
        help_text=_("Error message."),
    )
