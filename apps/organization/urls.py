# Third-party imports
from django.urls import path

# Project imports
from apps.organization.views import OrganizationCreateView
from apps.organization.views import OrganizationDetailView
from apps.organization.views import OrganizationLogoUploadView

# Set application namespace
app_name = "organization"

# Organization management URLs
urlpatterns = [
    # Organization creation URL
    path("", OrganizationCreateView.as_view(), name="organization-create"),
    # Organization detail URL
    path(
        "<str:organization_id>/",
        OrganizationDetailView.as_view(),
        name="organization-detail",
    ),
    # Organization logo upload URL
    path(
        "<str:organization_id>/logo/",
        OrganizationLogoUploadView.as_view(),
        name="organization-logo-upload",
    ),
]
