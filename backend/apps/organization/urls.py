# Third-party imports
from django.urls import path

# Local application imports
from apps.organization.views import (
    OrganizationCreateView,
    OrganizationDetailView,
    OrganizationLeaveView,
    OrganizationListView,
    OrganizationLogoUploadView,
    OrganizationMemberAddView,
    OrganizationMemberListView,
    OrganizationMemberRemoveView,
    OrganizationOwnershipTransferAcceptView,
    OrganizationOwnershipTransferCancelView,
    OrganizationOwnershipTransferInitView,
    OrganizationOwnershipTransferRejectView,
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
    # Organization leave URL
    path(
        "<str:organization_id>/leave/",
        OrganizationLeaveView.as_view(),
        name="organization-leave",
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
    # Organization ownership transfer initialization URL
    path(
        "<str:organization_id>/transfer/",
        OrganizationOwnershipTransferInitView.as_view(),
        name="organization-ownership-transfer-init",
    ),
    # Organization ownership transfer cancel URL
    path(
        "<str:organization_id>/transfer/cancel/",
        OrganizationOwnershipTransferCancelView.as_view(),
        name="organization-ownership-transfer-cancel",
    ),
    # Organization ownership transfer accept URL
    path(
        "transfer/<str:transfer_id>/accept/",
        OrganizationOwnershipTransferAcceptView.as_view(),
        name="organization-ownership-transfer-accept",
    ),
    # Organization ownership transfer reject URL
    path(
        "transfer/<str:transfer_id>/reject/",
        OrganizationOwnershipTransferRejectView.as_view(),
        name="organization-ownership-transfer-reject",
    ),
]
