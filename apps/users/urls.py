# Third
from django.urls import path

# Project imports
from apps.users.views import ResendActivationEmailView
from apps.users.views import UserActivationView
from apps.users.views import UserCreateView
from apps.users.views import UserDeactivateView
from apps.users.views import UserDeletionConfirmView
from apps.users.views import UserDeletionRequestView
from apps.users.views import UserLoginView
from apps.users.views import UserMeView
from apps.users.views import UserPasswordResetConfirmView
from apps.users.views import UserPasswordResetRequestView
from apps.users.views import UserReactivationConfirmView
from apps.users.views import UserReactivationRequestView
from apps.users.views import UserReloginView

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
