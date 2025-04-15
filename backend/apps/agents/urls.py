# Third-party imports
from django.urls import path

# Local application imports
from apps.agents.views import (
    AgentCreateView,
    AgentDeleteView,
    AgentDetailView,
    AgentListMeView,
    AgentListView,
    AgentUpdateView,
)

# Set application namespace
app_name = "agents"

# Agent management URLs
urlpatterns = [
    # Agent creation URL
    path("", AgentCreateView.as_view(), name="agent-create"),
    # Agent list URL - get all agents within an organization (organization_id required)
    path("list/", AgentListView.as_view(), name="agent-list"),
    # Agent list me URL - get all agents created by the current user (organization_id optional)
    path("list/me/", AgentListMeView.as_view(), name="agent-list-me"),
    # Agent detail URL - get an agent by ID
    path("<str:agent_id>/", AgentDetailView.as_view(), name="agent-detail"),
    # Agent update URL - update an agent by ID
    path("<str:agent_id>/update/", AgentUpdateView.as_view(), name="agent-update"),
    # Agent delete URL - delete an agent by ID
    path("<str:agent_id>/delete/", AgentDeleteView.as_view(), name="agent-delete"),
]
