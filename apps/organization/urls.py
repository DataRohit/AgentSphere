# Third-party imports
from django.urls import path

# Project imports
from apps.organization.views import OrganizationCreateView
from apps.organization.views import OrganizationLogoUploadView

# Set application namespace
app_name = "organization"

# Organization management URLs
urlpatterns = [
    # Organization creation URL
    path("", OrganizationCreateView.as_view(), name="organization-create"),
    # Organization logo upload URL
    path(
        "<str:organization_id>/logo/",
        OrganizationLogoUploadView.as_view(),
        name="organization-logo-upload",
    ),
]
