# Third-party imports
from django.urls import path

# Local application imports
from apps.conversation.views import SessionCreateView

# Set application namespace
app_name = "conversation"

# Conversation management URLs
urlpatterns = [
    # Session creation URL
    path("session/<str:chat_id>/", SessionCreateView.as_view(), name="session-create"),
]
