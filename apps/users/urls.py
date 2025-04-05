# Third
from django.urls import path

# Project imports
from apps.users.views import UserActivationView
from apps.users.views import UserCreateView

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
]
