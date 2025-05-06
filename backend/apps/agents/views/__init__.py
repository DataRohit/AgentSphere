# Local application imports
from apps.agents.views.agent_create import AgentCreateView
from apps.agents.views.agent_delete import AgentDeleteView
from apps.agents.views.agent_detail import AgentDetailView
from apps.agents.views.agent_list import AgentListView
from apps.agents.views.agent_list_me import AgentListMeView
from apps.agents.views.agent_update import AgentUpdateView

# Exports
__all__ = [
    "AgentCreateView",
    "AgentDeleteView",
    "AgentDetailView",
    "AgentListMeView",
    "AgentListView",
    "AgentUpdateView",
]
