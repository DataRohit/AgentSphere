# Standard library imports
import asyncio
import types

# Third-party imports
from django.db import transaction
from mcp import types as mcp_types
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

# Local application imports
from apps.tools.models import MCPServer, MCPTool


# MCP client
class MCPClient:
    """MCP Client for interacting with MCP servers.

    This class provides methods for connecting to an MCP server and
    retrieving information about the tools it provides.

    Attributes:
        server_url (str): The URL of the MCP server.
        _sse_context: The SSE context for the connection.
        _session: The client session.
        _streams: The streams for the connection.
    """

    # Initialize the MCP client
    def __init__(self, server_url: str):
        """Initialize the MCP client.

        Args:
            server_url (str): The URL of the MCP server.

        Raises:
            ValueError: If the server URL does not start with http:// or https://.
        """

        # Validate the server URL
        if not server_url.startswith(("http://", "https://")):
            # Set the error message
            error_message = "Server URL must start with http:// or https://"

            # Raise the error
            raise ValueError(error_message)

        # Set the server URL
        self.server_url = server_url

        # Initialize connection attributes
        self._sse_context = None
        self._session = None
        self._streams = None

    # Enter the async context manager
    async def __aenter__(self) -> "MCPClient":
        """Enter the async context manager.

        Returns:
            MCPClient: The MCP client instance.
        """

        # Create the SSE context
        self._sse_context = sse_client(self.server_url)

        # Enter the SSE context
        self._streams = await self._sse_context.__aenter__()

        # Create the client session
        self._session = ClientSession(self._streams[0], self._streams[1])

        # Enter the client session
        await self._session.__aenter__()

        # Initialize the session
        await self._session.initialize()

        # Return the client
        return self

    # Exit the async context manager
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Exit the async context manager.

        Args:
            exc_type (type[BaseException] | None): The exception type.
            exc_val (BaseException | None): The exception value.
            exc_tb (types.TracebackType | None): The exception traceback.
        """

        # Close the client
        await self.close()

    # Close the MCP client connection
    async def close(self):
        """Close the MCP client connection.

        This method closes the client session and SSE context.
        """

        # Close the client session
        if self._session is not None:
            # Exit the client session
            await self._session.__aexit__(None, None, None)

            # Clear the client session
            self._session = None

        # Close the SSE context
        if self._sse_context is not None:
            # Exit the SSE context
            await self._sse_context.__aexit__(None, None, None)

            # Clear the SSE context
            self._sse_context = None

        # Clear the streams
        self._streams = None

    # Ensure the client is connected
    async def _ensure_connected(self):
        """Ensure the client is connected.

        Raises:
            RuntimeError: If the client is not connected.
        """

        # Check if the client is connected
        if self._session is None or self._sse_context is None:
            # Set the error message
            error_message = "Client is not connected"

            # Raise the error
            raise RuntimeError(error_message)

    # List the tools provided by the MCP server
    async def list_tools(self) -> list[mcp_types.Tool]:
        """List the tools provided by the MCP server.

        Returns:
            list[mcp_types.Tool]: A list of tools provided by the MCP server.

        Raises:
            RuntimeError: If the client is not connected.
        """

        # Ensure the client is connected
        await self._ensure_connected()

        # Get the tools
        return await self._session.list_tools()


# Fetch tools from an MCP server
async def _fetch_tools_from_server(server_url: str) -> list[mcp_types.Tool] | None:
    """Fetch tools from an MCP server.

    Args:
        server_url (str): The URL of the MCP server.

    Returns:
        Optional[List[types.Tool]]: A list of tools provided by the MCP server,
            or None if an error occurred.
    """

    try:
        # Create the MCP client
        client = MCPClient(server_url)

        # Enter the client
        await client.__aenter__()

        # Connect to the server
        async with client:
            # Get the tools & return them
            return await client.list_tools().tools

    # Return None if an error occurred
    except (RuntimeError, Exception):
        return None


# Fetch tools from an MCP server and create MCPTool objects
def fetch_mcp_tools(mcpserver: MCPServer) -> bool:
    """Fetch tools from an MCP server and create MCPTool objects.

    This function fetches the tools from an MCP server and creates
    MCPTool objects for each tool.

    Args:
        mcpserver (MCPServer): The MCP server to fetch tools from.

    Returns:
        bool: True if tools were successfully fetched and created,
            False otherwise.
    """

    try:
        # Get the server URL
        server_url = mcpserver.url

        # Ensure the URL ends with /sse
        if not server_url.endswith("/sse"):
            # Set the server URL
            server_url = f"{server_url}/sse"

        # Run the async function to fetch tools
        tools = asyncio.run(_fetch_tools_from_server(server_url))

        # If no tools were found
        if not tools:
            # Return False
            return False

        # Create MCPTool objects for each tool
        with transaction.atomic():
            # Delete existing tools for this server
            MCPTool.objects.filter(mcpserver=mcpserver).delete()

            # Traverse the tools
            for tool in tools:
                # Create the MCPTool object
                MCPTool.objects.create(
                    name=tool.name,
                    description=tool.description or "",
                    mcpserver=mcpserver,
                )

    # Return False if an error occurred
    except (RuntimeError, Exception):
        return False

    # Return success
    return True
