# Third-party imports
from django.urls import path

# Project imports
from apps.tools.views import MCPServerCreateView, MCPServerDetailView, MCPServerListView

# Set application namespace
app_name = "org_tools"

# MCP Server management URLs
urlpatterns = [
    # MCP Server creation URL
    path("mcpserver/", MCPServerCreateView.as_view(), name="mcpserver-create"),
    # MCP Server list URL - organization ID is in the query parameters
    path("mcpserver/list/", MCPServerListView.as_view(), name="mcpserver-list"),
    # MCP Server detail URL - organization ID is in the request body
    path(
        "mcpserver/<str:organization_id>/<str:mcpserver_id>/",
        MCPServerDetailView.as_view(),
        name="mcpserver-detail",
    ),
]
