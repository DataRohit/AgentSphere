# Third-party imports
from django.urls import path

# Local application imports
from apps.llms.views import (
    LLMCreateView,
    LLMDeleteView,
    LLMDetailView,
    LLMListMeView,
    LLMListView,
    LLMModelsView,
    LLMUpdateView,
)

# Set application namespace
app_name = "llms"

# LLM management URLs
urlpatterns = [
    # LLM creation URL
    path("", LLMCreateView.as_view(), name="llm-create"),
    # LLM list URL - get all LLMs within an organization (organization_id required)
    path("list/", LLMListView.as_view(), name="llm-list"),
    # LLM list me URL - get all LLMs created by the current user (organization_id optional)
    path("list/me/", LLMListMeView.as_view(), name="llm-list-me"),
    # LLM models URL - get supported models for a specific API type
    path("models/<str:api_type>/", LLMModelsView.as_view(), name="llm-models"),
    # LLM detail URL - get an LLM by ID
    path("<str:llm_id>/", LLMDetailView.as_view(), name="llm-detail"),
    # LLM update URL - update an LLM by ID
    path("<str:llm_id>/update/", LLMUpdateView.as_view(), name="llm-update"),
    # LLM delete URL - delete an LLM by ID
    path("<str:llm_id>/delete/", LLMDeleteView.as_view(), name="llm-delete"),
]
