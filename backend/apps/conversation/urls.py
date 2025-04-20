# Third-party imports
from django.urls import path

# Local application imports
from apps.conversation.views import (
    SessionCountView,
    SessionCreateView,
    SessionDeactivateView,
    SessionDeleteView,
    SessionDetailView,
    SessionListView,
)

# Set application namespace
app_name = "conversation"

# Conversation management URLs
urlpatterns = [
    # Session creation URL
    path("session/", SessionCreateView.as_view(), name="session-create"),
    # Session list URL
    path("session/list/", SessionListView.as_view(), name="session-list"),
    # Session count URL
    path("session/count/", SessionCountView.as_view(), name="session-count"),
    # Session detail URL
    path("session/<str:session_id>/", SessionDetailView.as_view(), name="session-detail"),
    # Session deactivate URL
    path("session/<str:session_id>/deactivate/", SessionDeactivateView.as_view(), name="session-deactivate"),
    # Session delete URL
    path("session/<str:session_id>/delete/", SessionDeleteView.as_view(), name="session-delete"),
]
