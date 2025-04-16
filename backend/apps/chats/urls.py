# Third-party imports
from django.urls import path

# Local application imports
from apps.chats.views import SingleChatCreateView, SingleChatDetailView, SingleChatUpdateView

# Set application namespace
app_name = "chats"

# Chat management URLs
urlpatterns = [
    # Single chat creation URL
    path("single/", SingleChatCreateView.as_view(), name="single-chat-create"),
    # Single chat detail URL
    path("single/<str:single_chat_id>/", SingleChatDetailView.as_view(), name="single-chat-detail"),
    # Single chat update URL
    path("single/<str:single_chat_id>/update/", SingleChatUpdateView.as_view(), name="single-chat-update"),
]
