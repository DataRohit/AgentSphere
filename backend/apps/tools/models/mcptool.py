# Standard library imports
from django.db import models
from django.utils.translation import gettext_lazy as _

# Local application imports
from apps.common.models.timestamped import TimeStampedModel
from apps.tools.models.mcpserver import MCPServer


# MCPTool model
class MCPTool(TimeStampedModel):
    """Model for MCP Tools in the system.

    This model stores MCP Tool information including name and description.
    Each tool is associated with exactly one MCP Server.

    Attributes:
        name (CharField): The name of the MCP Tool.
        description (TextField): A detailed description of the tool.
        mcpserver (ForeignKey): The MCP Server this tool belongs to.

    Meta:
        verbose_name (str): Human-readable name for the model.
        verbose_name_plural (str): Human-readable plural name for the model.
        ordering (list): Default ordering for model instances.
        db_table (str): The database table name.
    """

    # Tool name
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
    )

    # Tool description
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
    )

    # MCP Server the tool belongs to
    mcpserver = models.ForeignKey(
        MCPServer,
        verbose_name=_("MCP Server"),
        on_delete=models.CASCADE,
        related_name="tools",
    )

    # Meta class for MCPTool model configuration
    class Meta:
        """Meta class for MCPTool model configuration.

        Attributes:
            verbose_name (str): Human-readable name for the model.
            verbose_name_plural (str): Human-readable plural name for the model.
            ordering (list): Default ordering for model instances.
            db_table (str): The database table name.
        """

        # Human-readable model name
        verbose_name = _("MCP Tool")

        # Human-readable plural model name
        verbose_name_plural = _("MCP Tools")

        # Default ordering by name
        ordering = ["name"]

        # Specify the database table name
        db_table = "tools_mcptool"

    # String representation of the MCPTool
    def __str__(self) -> str:
        """Return a string representation of the MCPTool.

        Returns:
            str: The name of the MCPTool.
        """

        # Return the name of the MCPTool
        return self.name
