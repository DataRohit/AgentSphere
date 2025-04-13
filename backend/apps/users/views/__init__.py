# Project imports
from apps.users.views.resend_activation import ResendActivationEmailView
from apps.users.views.user_activation import UserActivationView
from apps.users.views.user_avatar_upload import UserAvatarUploadView
from apps.users.views.user_create import UserCreateView
from apps.users.views.user_deactivate import UserDeactivateView
from apps.users.views.user_deletion import (
    UserDeletionConfirmView,
    UserDeletionRequestView,
)
from apps.users.views.user_login import UserLoginView
from apps.users.views.user_me import UserMeView
from apps.users.views.user_password_reset import (
    UserPasswordResetConfirmView,
    UserPasswordResetRequestView,
)
from apps.users.views.user_reactivation import (
    UserReactivationConfirmView,
    UserReactivationRequestView,
)
from apps.users.views.user_relogin import UserReloginView

# Exports
__all__ = [
    "ResendActivationEmailView",
    "UserActivationView",
    "UserAvatarUploadView",
    "UserCreateView",
    "UserDeactivateView",
    "UserDeletionConfirmView",
    "UserDeletionRequestView",
    "UserLoginView",
    "UserMeView",
    "UserPasswordResetConfirmView",
    "UserPasswordResetRequestView",
    "UserReactivationConfirmView",
    "UserReactivationRequestView",
    "UserReloginView",
]
