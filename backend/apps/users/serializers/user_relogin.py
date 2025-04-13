# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer


# User relogin serializer (extends TokenRefreshSerializer)
class UserReloginSerializer(TokenRefreshSerializer):
    """User relogin serializer.

    This serializer handles refreshing JWT access tokens.
    It extends the TokenRefreshSerializer to provide better documentation.

    Attributes:
        refresh (str): The refresh token for obtaining new access tokens.
    """

    # Refresh token field with better documentation
    refresh = serializers.CharField(
        help_text=_("Refresh token for obtaining new access tokens."),
    )


# User relogin response serializer
class UserReloginResponseSerializer(serializers.Serializer):
    """User relogin response serializer.

    This serializer defines the structure of the token refresh response.

    Attributes:
        access (str): The new access token for authenticating API requests.
    """

    # Access token field
    access = serializers.CharField(
        help_text=_("New access token for authenticating API requests."),
        read_only=True,
    )


# User relogin error response serializer
class UserReloginErrorResponseSerializer(serializers.Serializer):
    """User relogin error response serializer.

    This serializer defines the structure of the token refresh error response.

    Attributes:
        error (str): The error message.
    """

    # Error message field
    error = serializers.CharField(
        help_text=_("Error message for token refresh failure."),
        read_only=True,
    )
