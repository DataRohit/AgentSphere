# Third-party imports
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer
from apps.users.serializers.user_profile import UserProfileSerializer

# Get the user model
User = get_user_model()


# User profile update serializer
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """User profile update serializer.

    This serializer handles updating the authenticated user's profile.
    Users can update their username, first name, and last name.

    Attributes:
        username (str): The user's username.
        first_name (str): The user's first name.
        last_name (str): The user's last name.

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
            "username",
            "first_name",
            "last_name",
        ]

    # Validate the username to ensure it's unique
    def validate_username(self, value: str) -> str:
        """Validate that the username is unique.

        Args:
            value (str): The username to validate.

        Returns:
            str: The validated username.

        Raises:
            serializers.ValidationError: If the username is already taken by another user.
        """

        # Get the current user from the context
        user = self.context["request"].user

        # Check if username is taken by another user
        if User.objects.filter(username=value).exclude(id=user.id).exists():
            # Raise a validation error if the username is already taken
            raise serializers.ValidationError(
                _("This username is already taken."),
                code=status.HTTP_400_BAD_REQUEST,
            ) from None

        # Return the validated username
        return value


# User profile update success response serializer
class UserProfileUpdateResponseSerializer(GenericResponseSerializer):
    """User profile update success response serializer.

    This serializer defines the structure of the successful profile update response.

    Attributes:
        status_code (int): The status code of the response.
        user (UserProfileSerializer): The updated user profile data.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
    )

    # User profile
    user = UserProfileSerializer(
        help_text=_("Updated user profile data."),
        read_only=True,
    )


# User profile update error response serializer
class UserProfileUpdateErrorResponseSerializer(GenericResponseSerializer):
    """User profile update error response serializer.

    This serializer defines the structure of the profile update error response.

    Attributes:
        status_code (int): The HTTP status code.
        errors (UserProfileUpdateErrorsSerializer): The validation errors.
    """

    # Nested serializer for validation errors
    class UserProfileUpdateErrorsSerializer(serializers.Serializer):
        """User profile update errors serializer.

        Attributes:
            username (list): Errors related to the username field.
            first_name (list): Errors related to the first name field.
            last_name (list): Errors related to the last name field.
            non_field_errors (list): Non-field specific errors.
        """

        # Username field errors
        username = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the username field."),
        )

        # First name field errors
        first_name = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the first name field."),
        )

        # Last name field errors
        last_name = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the last name field."),
        )

        # Non-field errors
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Non-field specific errors."),
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        help_text=_("HTTP status code indicating validation errors."),
        read_only=True,
    )

    # Errors
    errors = UserProfileUpdateErrorsSerializer(
        help_text=_("Object containing validation errors."),
    )
