# Third-party imports
from django.urls import path

# Local application imports
from apps.agents.views import (
    AgentCreateView,
    AgentDeleteView,
    AgentListMeView,
    AgentListView,
    AgentUpdateView,
    MostActiveAgentsView,
    MostUsedAgentsView,
)

# Set application namespace
app_name = "agents"

# Agent management URLs
urlpatterns = [
    # Agent creation URL
    path("", AgentCreateView.as_view(), name="agent-create"),
    # Agent list URL - get agents by user within an organization (organization_id and username required)
    path("list/", AgentListView.as_view(), name="agent-list"),
    # Agent list me URL - get all agents created by the current user (organization_id required)
    path("list/me/", AgentListMeView.as_view(), name="agent-list-me"),
    # Most used agents URL - get the top 3 most used agents
    path("stats/most-used/", MostUsedAgentsView.as_view(), name="agent-most-used"),
    # Most active agents URL - get the top 3 most active agents
    path("stats/most-active/", MostActiveAgentsView.as_view(), name="agent-most-active"),
    # Agent update URL - update an agent by ID
    path("<str:agent_id>/update/", AgentUpdateView.as_view(), name="agent-update"),
    # Agent delete URL - delete an agent by ID
    path("<str:agent_id>/delete/", AgentDeleteView.as_view(), name="agent-delete"),
]
