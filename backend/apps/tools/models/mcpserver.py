# Third-party imports
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

# Local application imports
from apps.common.models.timestamped import TimeStampedModel
from apps.organization.models import Organization
from apps.tools.utils.mcp_client import fetch_mcp_tools

# Get the User model
User = get_user_model()


# MCPServer model
class MCPServer(TimeStampedModel):
    """Model for MCP Servers in the system.

    This model stores MCP Server information including name, description,
    and URL. A user can create a maximum of 5 MCP Servers per organization.

    Attributes:
        name (CharField): The name of the MCP Server.
        description (TextField): A detailed description of the server.
        url (URLField): The URL of the MCP Server.
        organization (ForeignKey): The organization this server belongs to.
        user (ForeignKey): The user who created this server.
        tags (CharField): Optional tags for categorizing the server.

    Meta:
        verbose_name (str): Human-readable name for the model.
        verbose_name_plural (str): Human-readable plural name for the model.
        ordering (list): Default ordering for model instances.
        db_table (str): The database table name.
    """

    # Maximum number of MCP Servers a user can create per organization
    MAX_MCPSERVERS_PER_USER_PER_ORGANIZATION = 5

    # Server name
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
    )

    # Server description
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
    )

    # Server URL
    url = models.URLField(
        verbose_name=_("URL"),
        max_length=255,
        unique=True,
    )

    # Optional tags
    tags = models.CharField(
        verbose_name=_("Tags"),
        max_length=255,
        blank=True,
        help_text=_("Comma-separated tags for categorizing the server"),
    )

    # Organization the server belongs to
    organization = models.ForeignKey(
        Organization,
        verbose_name=_("Organization"),
        on_delete=models.CASCADE,
        related_name="mcp_servers",
    )

    # User who created the server
    user = models.ForeignKey(
        User,
        verbose_name=_("Created By"),
        on_delete=models.CASCADE,
        related_name="created_mcp_servers",
    )

    # Meta class for MCPServer model configuration
    class Meta:
        """Meta class for MCPServer model configuration.

        Attributes:
            verbose_name (str): Human-readable name for the model.
            verbose_name_plural (str): Human-readable plural name for the model.
            ordering (list): Default ordering for model instances.
            db_table (str): The database table name.
        """

        # Human-readable model name
        verbose_name = _("MCP Server")

        # Human-readable plural model name
        verbose_name_plural = _("MCP Servers")

        # Default ordering by name
        ordering = ["name"]

        # Specify the database table name
        db_table = "tools_mcpserver"

    # String representation of the MCPServer
    def __str__(self) -> str:
        """Return a string representation of the MCPServer.

        Returns:
            str: The name of the MCPServer.
        """

        # Return the name of the MCPServer
        return self.name

    # Save the MCPServer instance
    def save(self, *args, **kwargs):
        """Save the MCPServer instance.

        This method overrides the default save method to fetch tools
        from the MCP server when a new server is created.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """

        # Save the instance
        super().save(*args, **kwargs)

        # Fetch tools from the MCP server
        fetch_mcp_tools(self)
