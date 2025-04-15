# Third
from django.urls import path

# Local application imports
from apps.users.views import (
    ResendActivationEmailView,
    UserActivationView,
    UserAvatarUploadView,
    UserCreateView,
    UserDeactivateView,
    UserDeletionConfirmView,
    UserDeletionRequestView,
    UserLoginView,
    UserMeView,
    UserPasswordResetConfirmView,
    UserPasswordResetRequestView,
    UserReactivationConfirmView,
    UserReactivationRequestView,
    UserReloginView,
)

# Set application namespace
app_name = "users"

# User management URLs
urlpatterns = [
    # User creation URL
    path("", UserCreateView.as_view(), name="user-create"),
    # User activation URL
    path(
        "activate/<str:uid>/<str:token>/",
        UserActivationView.as_view(),
        name="user-activation",
    ),
    # Resend activation email URL
    path(
        "resend-activation/",
        ResendActivationEmailView.as_view(),
        name="user-resend-activation",
    ),
    # Login URL
    path("login/", UserLoginView.as_view(), name="user-login"),
    # Relogin URL
    path("relogin/", UserReloginView.as_view(), name="user-relogin"),
    # User profile URL
    path("me/", UserMeView.as_view(), name="user-me"),
    # User avatar upload URL
    path("me/avatar/", UserAvatarUploadView.as_view(), name="user-avatar-upload"),
    # User deactivation URL
    path("deactivate/", UserDeactivateView.as_view(), name="user-deactivate"),
    # User reactivation request URL
    path(
        "reactivate/",
        UserReactivationRequestView.as_view(),
        name="user-reactivation-request",
    ),
    # User reactivation confirmation URL
    path(
        "reactivate/<str:uid>/<str:token>/",
        UserReactivationConfirmView.as_view(),
        name="user-reactivation-confirm",
    ),
    # User deletion request URL
    path(
        "delete/",
        UserDeletionRequestView.as_view(),
        name="user-deletion-request",
    ),
    # User deletion confirmation URL
    path(
        "delete/<str:uid>/<str:token>/",
        UserDeletionConfirmView.as_view(),
        name="user-deletion-confirm",
    ),
    # User password reset request URL
    path(
        "password-reset/",
        UserPasswordResetRequestView.as_view(),
        name="user-password-reset-request",
    ),
    # User password reset confirmation URL
    path(
        "password-reset/<str:uid>/<str:token>/",
        UserPasswordResetConfirmView.as_view(),
        name="user-password-reset-confirm",
    ),
]
