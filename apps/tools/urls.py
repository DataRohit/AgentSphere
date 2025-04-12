# Third-party imports
from django.urls import path

# Project imports
from apps.tools.views import MCPServerCreateView, MCPServerListView

# Set application namespace
app_name = "org_tools"

# Organization-specific MCP Server management URLs
urlpatterns = [
    # MCP Server creation URL
    path("mcpserver/", MCPServerCreateView.as_view(), name="mcpserver-create"),
    # MCP Server list URL
    path("mcpserver/list/", MCPServerListView.as_view(), name="mcpserver-list"),
]
