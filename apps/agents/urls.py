# Third-party imports
from django.urls import path

# Local application imports
from apps.agents.views import AgentCreateView

# Set application namespace
app_name = "agents"

# Agent management URLs
urlpatterns = [
    # Agent creation URL
    path("", AgentCreateView.as_view(), name="agent-create"),
]
