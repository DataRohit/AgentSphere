# Third-party imports
from django.urls import path

# Project imports
from apps.tools.views import MCPServerCreateView

# Set application namespace
app_name = "org_tools"

# Organization-specific MCP Server management URLs
urlpatterns = [
    # MCP Server creation URL
    path("mcpserver/", MCPServerCreateView.as_view(), name="mcpserver-create"),
]
