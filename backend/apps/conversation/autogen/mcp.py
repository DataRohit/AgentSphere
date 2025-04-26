# Third party imports
from asgiref.sync import sync_to_async
from autogen_ext.tools.mcp import SseMcpToolAdapter, SseServerParams

# Local application imports
from apps.agents.models import Agent
from apps.tools.models import MCPServer


# Function to create an MCP tool adapter for a given MCP server
async def create_mcp_tool_adapter(mcp_server: MCPServer, tool_name: str | None = None) -> SseMcpToolAdapter | None:
    """Create an MCP tool adapter for a given MCP server.

    Args:
        mcp_server (MCPServer): The MCP server to create an adapter for.
        tool_name (str | None, optional): The name of the tool to create an adapter for.
            If None, the first tool associated with the server will be used.

    Returns:
        SseMcpToolAdapter | None: The created adapter, or None if creation failed.
    """

    try:
        # Create server params for the MCP server
        server_params = SseServerParams(
            url=mcp_server.url,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        # If no specific tool name is provided, try to get the first tool
        if tool_name is None:
            # Get the first tool for this server
            tool = await sync_to_async(lambda s=mcp_server: s.tools.first())()

            # If no tools are available
            if tool is None:
                # Return None
                return None

            # Use the name of the first tool
            tool_name = tool.name

        # Create the adapter from server params
        adapter = await SseMcpToolAdapter.from_server_params(server_params, tool_name)

    except (ValueError, TypeError, AttributeError):
        # If there's any error creating the adapter, return None
        return None

    # Return the adapter
    return adapter


# Function to get MCP tools for an agent
async def get_mcp_tools_for_agent(agent_id: str) -> list[SseMcpToolAdapter]:
    """Get MCP tools for an agent.

    Args:
        agent_id (str): The ID of the agent.

    Returns:
        list[SseMcpToolAdapter]: List of MCP tool adapters.
    """

    # Convert the synchronous database query to async
    @sync_to_async
    def get_mcp_servers(agent_id: str) -> list[MCPServer]:
        try:
            # Get the agent
            agent = Agent.objects.get(id=agent_id)

            # Return the MCP servers
            return list(agent.mcp_servers.all())

        except Agent.DoesNotExist:
            # If the agent does not exist, return an empty list
            return []

    # Get the MCP servers for the agent
    mcp_servers = await get_mcp_servers(agent_id)

    # List to store the tools
    tools = []

    # Create adapters for each MCP server
    for server in mcp_servers:
        # Get all tools for this server asynchronously
        server_tools = await sync_to_async(lambda s=server: list(s.tools.all()))()

        # If the server has tools
        if server_tools:
            # Create an adapter for each tool
            for tool in server_tools:
                # Create the adapter with the specific tool name
                adapter = await create_mcp_tool_adapter(server, tool.name)

                # If the adapter was created successfully
                if adapter:
                    # Add the adapter to the list
                    tools.append(adapter)

        else:
            # If no specific tools found, try to create a default adapter
            adapter = await create_mcp_tool_adapter(server)

            # If the adapter was created successfully
            if adapter:
                # Add the adapter to the list
                tools.append(adapter)

    # Return the tools
    return tools
