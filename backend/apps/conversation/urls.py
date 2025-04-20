# Third-party imports
from django.urls import path

# Local application imports
from apps.conversation.views import SessionCreateView, SessionDeactivateView, SessionDetailView

# Set application namespace
app_name = "conversation"

# Conversation management URLs
urlpatterns = [
    # Session creation URL
    path("session/", SessionCreateView.as_view(), name="session-create"),
    # Session detail URL
    path("session/<str:session_id>/", SessionDetailView.as_view(), name="session-detail"),
    # Session deactivate URL
    path("session/<str:session_id>/deactivate/", SessionDeactivateView.as_view(), name="session-deactivate"),
]
