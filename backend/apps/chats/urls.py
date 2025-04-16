# Third-party imports
from django.urls import path

# Local application imports
from apps.chats.views import (
    SingleChatCreateView,
    SingleChatDeleteView,
    SingleChatDetailView,
    SingleChatsListView,
    SingleChatUpdateView,
)

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
    # Single chat delete URL
    path("single/<str:single_chat_id>/delete/", SingleChatDeleteView.as_view(), name="single-chat-delete"),
    # Single chats list URL
    path("single/list/", SingleChatsListView.as_view(), name="single-chats-list"),
]
