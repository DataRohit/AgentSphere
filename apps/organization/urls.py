# Third-party imports
from django.urls import path

# Project imports
from apps.organization.views import (
    OrganizationCreateView,
    OrganizationDetailView,
    OrganizationListView,
    OrganizationLogoUploadView,
    OrganizationMemberAddByEmailView,
    OrganizationMemberAddByIdView,
    OrganizationMemberAddByUsernameView,
    OrganizationMemberListView,
    OrganizationMemberRemoveByEmailView,
    OrganizationMemberRemoveByIdView,
    OrganizationMemberRemoveByUsernameView,
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
    # Organization member add by ID URL
    path(
        "<str:organization_id>/members/add/by-id/",
        OrganizationMemberAddByIdView.as_view(),
        name="organization-member-add-by-id",
    ),
    # Organization member add by email URL
    path(
        "<str:organization_id>/members/add/by-email/",
        OrganizationMemberAddByEmailView.as_view(),
        name="organization-member-add-by-email",
    ),
    # Organization member add by username URL
    path(
        "<str:organization_id>/members/add/by-username/",
        OrganizationMemberAddByUsernameView.as_view(),
        name="organization-member-add-by-username",
    ),
    # Organization member remove by ID URL
    path(
        "<str:organization_id>/members/remove/by-id/",
        OrganizationMemberRemoveByIdView.as_view(),
        name="organization-member-remove-by-id",
    ),
    # Organization member remove by email URL
    path(
        "<str:organization_id>/members/remove/by-email/",
        OrganizationMemberRemoveByEmailView.as_view(),
        name="organization-member-remove-by-email",
    ),
    # Organization member remove by username URL
    path(
        "<str:organization_id>/members/remove/by-username/",
        OrganizationMemberRemoveByUsernameView.as_view(),
        name="organization-member-remove-by-username",
    ),
]
