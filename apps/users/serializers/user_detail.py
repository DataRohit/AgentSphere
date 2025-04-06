# Third-party imports
from django.contrib.auth import get_user_model
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
        is_active (bool): Whether the user is active.
        is_staff (bool): Whether the user is a staff member.
        is_superuser (bool): Whether the user is a superuser.
        date_joined (datetime): The date and time the user joined the system.
        last_login (datetime): The date and time the user last logged in.

    Meta:
        model (User): The User model.
        fields (list): The fields to include in the serializer.
    """

    # Meta class
    class Meta:
        # Model to use for the serializer
        model = User

        # Fields to include in the serializer
        fields = [
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
        ]
