# Third-party imports
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer

# Get the user model
User = get_user_model()


# User profile serializer
class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer.

    This serializer provides a detailed representation of the authenticated user's profile.

    Attributes:
        id (UUID): The user's ID.
        email (str): The user's email address.
        username (str): The user's username.
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        full_name (str): The user's full name.
        avatar_url (str): The user's avatar URL.
        is_active (bool): Whether the user is active.
        is_staff (bool): Whether the user is a staff member.
        is_superuser (bool): Whether the user is a superuser.
        date_joined (datetime): The date and time the user joined the system.
        last_login (datetime): The date and time the user last logged in.
    """

    # Full name field
    full_name = serializers.CharField(
        help_text=_("User's full name."),
        read_only=True,
    )

    # Avatar URL field
    avatar_url = serializers.SerializerMethodField(
        help_text=_("User's avatar URL."),
        read_only=True,
    )

    # Meta class
    class Meta:
        # Model to use for the serializer
        model = User

        # Fields to include in the serializer
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "avatar_url",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
        ]

        # Extra kwargs
        extra_kwargs = {
            "id": {"read_only": True},
            "email": {"read_only": True},
            "username": {"read_only": True},
            "first_name": {"read_only": True},
            "last_name": {"read_only": True},
            "avatar_url": {"read_only": True},
            "is_active": {"read_only": True},
            "is_staff": {"read_only": True},
            "is_superuser": {"read_only": True},
            "date_joined": {"read_only": True},
            "last_login": {"read_only": True},
        }

    # Get the avatar URL
    def get_avatar_url(self, obj: User) -> str:
        """Get the avatar URL for the user.

        Returns the avatar_url property from the user instance,
        which will return either the actual avatar URL or the default DiceBear URL.

        Args:
            obj: The user instance.

        Returns:
            str: The URL of the user's avatar.
        """

        # Return the avatar URL
        return obj.avatar_url


# User profile error response serializer
class UserProfileErrorResponseSerializer(serializers.Serializer):
    """User profile error response serializer.

    This serializer defines the structure of the profile error response.

    Attributes:
        status_code (int): The HTTP status code.
        error (str): The error message.
    """

    # Status code field
    status_code = serializers.IntegerField(
        default=status.HTTP_401_UNAUTHORIZED,
        help_text=_("HTTP status code for the response."),
        read_only=True,
    )

    # Error message field
    error = serializers.CharField(
        help_text=_("Error message for profile retrieval failure."),
        read_only=True,
    )


# User profile response serializer for proper Swagger documentation
class UserProfileResponseSerializer(GenericResponseSerializer):
    """User profile response serializer.

    This serializer defines the structure of the user profile response as it will
    be formatted by the GenericJSONRenderer.

    Attributes:
        status_code (int): The status code of the response.
        user (UserProfileSerializer): The user profile data.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
    )

    # User profile
    user = UserProfileSerializer(
        help_text=_("User profile data."),
        read_only=True,
    )
