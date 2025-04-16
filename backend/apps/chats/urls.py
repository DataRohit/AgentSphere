# Third-party imports
from django.urls import path

# Local application imports
from apps.chats.views import SingleChatCreateView

# Set application namespace
app_name = "chats"

# Chat management URLs
urlpatterns = [
    # Single chat creation URL
    path("single/", SingleChatCreateView.as_view(), name="single-chat-create"),
]
