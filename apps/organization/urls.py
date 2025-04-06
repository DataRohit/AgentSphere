# Third-party imports
from django.urls import path

# Project imports
from apps.organization.views import (
    OrganizationCreateView,
    OrganizationDetailView,
    OrganizationListView,
    OrganizationLogoUploadView,
    OrganizationMemberAddView,
    OrganizationMemberListView,
    OrganizationMemberRemoveView,
)

# Set application namespace
app_name = "organization"

# Organization management URLs
urlpatterns = [
    # Organization creation URL
    path("", OrganizationCreateView.as_view(), name="organization-create"),
    # Organization list URL (get all owned organizations)
    path("owned/", OrganizationListView.as_view(), name="organization-list-owned"),
    # Organization member list URL (get all organizations where the user is a member)
    path(
        "memberships/",
        OrganizationMemberListView.as_view(),
        name="organization-list-memberships",
    ),
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
    # Organization member add URL (unified: accepts user_id, email, or username)
    path(
        "<str:organization_id>/members/add/",
        OrganizationMemberAddView.as_view(),
        name="organization-member-add",
    ),
    # Organization member remove URL (unified: accepts user_id, email, or username)
    path(
        "<str:organization_id>/members/remove/",
        OrganizationMemberRemoveView.as_view(),
        name="organization-member-remove",
    ),
]
