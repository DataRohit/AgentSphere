# Third
from django.urls import path

# Project imports
from apps.users.views import ResendActivationEmailView
from apps.users.views import UserActivationView
from apps.users.views import UserCreateView
from apps.users.views import UserDeactivateView
from apps.users.views import UserLoginView
from apps.users.views import UserMeView
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
]
