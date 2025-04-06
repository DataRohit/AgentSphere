# Third-party imports
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

# Get the user model
User = get_user_model()


# User detail serializer
class UserDetailSerializer(serializers.ModelSerializer):
    """User detail serializer.

    This serializer provides a detailed representation of a user's account information.
    It includes fields for the user's ID, username, email, first name, last name,
    is_active status, is_staff status, is_superuser status, date joined, and last login.

    Attributes:
        pk (int): The user's ID.
        username (str): The user's username.
        email (str): The user's email address.
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        avatar_url (str): The user's avatar URL.
        is_active (bool): Whether the user is active.
        is_staff (bool): Whether the user is a staff member.
        is_superuser (bool): Whether the user is a superuser.
        date_joined (datetime): The date and time the user joined the system.
        last_login (datetime): The date and time the user last logged in.

    Meta:
        model (User): The User model.
        fields (list): The fields to include in the serializer.
    """

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
            "email",
            "first_name",
            "last_name",
            "username",
            "avatar_url",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
        ]

    def get_avatar_url(self, obj):
        """Get the avatar URL for the user.

        Returns the avatar_url property from the user instance,
        which will return either the actual avatar URL or the default DiceBear URL.

        Args:
            obj: The user instance.

        Returns:
            str: The URL of the user's avatar.
        """
        return obj.avatar_url
