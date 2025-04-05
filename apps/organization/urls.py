# Third-party imports
from django.urls import path

# Project imports
from apps.organization.views import OrganizationCreateView

# Set application namespace
app_name = "organization"

# Organization management URLs
urlpatterns = [
    # Organization creation URL
    path("", OrganizationCreateView.as_view(), name="organization-create"),
]
