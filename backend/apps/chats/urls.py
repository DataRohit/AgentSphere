# Third-party imports
from django.urls import path

# Local application imports
from apps.chats.views import (
    GroupChatCreateView,
    GroupChatDetailView,
    GroupChatsListMeView,
    GroupChatsListView,
    GroupChatUpdateView,
    SingleChatCreateView,
    SingleChatDeleteView,
    SingleChatDetailView,
    SingleChatsListMeView,
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
    # Single chats list for current user URL
    path("single/list/me/", SingleChatsListMeView.as_view(), name="single-chats-list-me"),
    # Group chat creation URL
    path("group/", GroupChatCreateView.as_view(), name="group-chat-create"),
    # Group chat detail URL
    path("group/<str:group_chat_id>/", GroupChatDetailView.as_view(), name="group-chat-detail"),
    # Group chat update URL
    path("group/<str:group_chat_id>/update/", GroupChatUpdateView.as_view(), name="group-chat-update"),
    # Group chats list URL
    path("group/list/", GroupChatsListView.as_view(), name="group-chats-list"),
    # Group chats list for current user URL
    path("group/list/me/", GroupChatsListMeView.as_view(), name="group-chats-list-me"),
]
