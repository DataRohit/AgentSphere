# Third-party imports
from django.urls import path

# Local application imports
from apps.agents.views import AgentCreateView, AgentDetailView, AgentListView

# Set application namespace
app_name = "agents"

# Agent management URLs
urlpatterns = [
    # Agent creation URL
    path("", AgentCreateView.as_view(), name="agent-create"),
    # Agent list URL - get all agents created by the user
    path("list/", AgentListView.as_view(), name="agent-list"),
    # Agent detail URL - get an agent by ID
    path("<str:agent_id>/", AgentDetailView.as_view(), name="agent-detail"),
]
