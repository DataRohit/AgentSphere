# Third-party imports
from django.urls import path

# Project imports
from apps.tools.views import (
    MCPServerCreateView,
    MCPServerDeleteView,
    MCPServerDetailView,
    MCPServerListMeView,
    MCPServerListView,
    MCPServerUpdateView,
)

# Set application namespace
app_name = "org_tools"

# MCP Server management URLs
urlpatterns = [
    # MCP Server creation URL
    path("mcpserver/", MCPServerCreateView.as_view(), name="mcpserver-create"),
    # MCP Server list URL - get all MCP servers within an organization (organization_id required)
    path("mcpserver/list/", MCPServerListView.as_view(), name="mcpserver-list"),
    # MCP Server list me URL - get all MCP servers created by the current user (organization_id optional)
    path("mcpserver/list/me/", MCPServerListMeView.as_view(), name="mcpserver-list-me"),
    # MCP Server detail URL - get an MCP server by ID
    path(
        "mcpserver/<str:mcpserver_id>/",
        MCPServerDetailView.as_view(),
        name="mcpserver-detail",
    ),
    # MCP Server update URL - update an MCP server by ID
    path(
        "mcpserver/<str:mcpserver_id>/update/",
        MCPServerUpdateView.as_view(),
        name="mcpserver-update",
    ),
    # MCP Server delete URL - delete an MCP server by ID
    path(
        "mcpserver/<str:mcpserver_id>/delete/",
        MCPServerDeleteView.as_view(),
        name="mcpserver-delete",
    ),
]
