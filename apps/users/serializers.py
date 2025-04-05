# Standard library imports
from typing import Any

# Third-party imports
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework import status

# Project imports
from apps.common.serializer import GenericResponseSerializer

# Get the user model
User = get_user_model()


# User creation serializer
class UserCreateSerializer(serializers.ModelSerializer):
    """User creation serializer.

    This serializer handles the creation of new user accounts. It validates the
    provided password and ensures that the email is unique.

    Attributes:
        re_password (str): Confirmation password field.

    Meta:
        model (User): The User model.
        fields (list): The fields to include in the serializer.

    Raises:
        serializers.ValidationError: If passwords do not match.

    Returns:
        User: The newly created user instance.
    """

    # Confirmation password field
    re_password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        help_text=_("Confirm password"),
        label=_("Password Confirmation"),
    )

    # Meta class
    class Meta:
        # Model to use for the serializer
        model = User

        # Fields to include in the serializer
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "re_password",
        ]

        # Extra kwargs
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}},
            User.USERNAME_FIELD: {"required": True, "allow_blank": False},
            "email": {
                "required": "email" in User.REQUIRED_FIELDS
                or User.USERNAME_FIELD == "email",
                "allow_blank": False,
            },
            "first_name": {
                "required": "first_name" in User.REQUIRED_FIELDS,
                "allow_blank": False,
            },
            "last_name": {
                "required": "last_name" in User.REQUIRED_FIELDS,
                "allow_blank": False,
            },
        }

    # Validate the user data
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate the user data.

        This method checks that the provided password and confirmation password match.

        Args:
            attrs (dict[str, Any]): The user data to validate.

        Raises:
            serializers.ValidationError: If passwords do not match.

        Returns:
            dict[str, Any]: The validated user data.
        """

        # Check that the password and confirmation password match
        if attrs["password"] != attrs["re_password"]:
            # Raise a validation error if they don't match
            raise serializers.ValidationError(
                {"password": _("Passwords do not match.")},
                code=status.HTTP_400_BAD_REQUEST,
            )

        # Return the validated user data
        return attrs

    # Create a new user instance
    def create(self, validated_data: dict[str, Any]) -> User:
        """Create a new user instance, setting password correctly.

        This method creates a new user instance and sets the password correctly.

        Args:
            validated_data (dict[str, Any]): The validated user data.

        Returns:
            User: The newly created user instance.
        """

        # Pop the confirmation password from the validated data
        validated_data.pop("re_password")

        # Create a new user instance & return it
        return User.objects.create_user(**validated_data, is_active=False)


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


# User creation success response serializer
class UserCreateSuccessResponseSerializer(GenericResponseSerializer):
    """User creation success response serializer.

    This serializer defines the structure of the successful user creation response.
    It includes a status code and a user detail serializer.

    Attributes:
        status_code (int): The status code of the response.
        user (UserDetailSerializer): The user detail serializer.
    """

    # Status code
    status_code = serializers.IntegerField(default=status.HTTP_201_CREATED)

    # User detail serializer
    user = UserDetailSerializer(
        read_only=True,
        help_text=_("Details of the created user."),
    )


# User creation error response serializer
class UserCreateErrorResponseSerializer(GenericResponseSerializer):
    """User creation error response serializer (for schema).

    This serializer defines the structure of the wrapped validation error response (400 Bad Request)
    as it would be formatted if GenericResponseSerializer handled errors, for documentation purposes.
    Actual 400 responses from the view are typically not wrapped by GenericJSONRenderer.

    Attributes:
        status_code (int): The status code of the response.
        errors (ErrorsDetailSerializer): The errors detail serializer.
    """

    # Nested serializer defining the structure of the actual errors
    class ErrorsDetailSerializer(serializers.Serializer):
        username = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the username field."),
        )
        email = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the email field."),
        )
        first_name = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the first name field."),
        )
        last_name = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the last name field."),
        )
        password = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the password field."),
        )
        re_password = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the password confirmation field."),
        )
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Non-field specific errors."),
        )

    # Override status_code from GenericResponseSerializer
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        help_text=_("HTTP status code indicating a bad request."),
    )

    # Define the 'errors' field containing the validation error details
    errors = ErrorsDetailSerializer(help_text=_("Object containing validation errors."))


# User activation success response serializer
class UserActivationSuccessResponseSerializer(GenericResponseSerializer):
    """User activation success response serializer.

    This serializer defines the structure of the successful user activation response.
    It includes a status code and an activation object with a message.

    Attributes:
        status_code (int): The status code of the response.
        activation (ActivationDataSerializer): The activation data.
    """

    # Nested serializer for the activation data
    class ActivationDataSerializer(serializers.Serializer):
        """Activation data serializer.

        This serializer defines the structure of the activation data.

        Attributes:
            message (str): A success message.
        """

        # Success message
        message = serializers.CharField(
            default=_("Account activated successfully"),
            help_text=_("Success message for account activation."),
            read_only=True,
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
    )

    # Activation data
    activation = ActivationDataSerializer(
        help_text=_("Activation data containing success message."),
        read_only=True,
    )


# User activation forbidden response serializer
class UserActivationForbiddenResponseSerializer(GenericResponseSerializer):
    """User activation forbidden response serializer.

    This serializer defines the structure of the forbidden response for user activation
    when a token has expired or has already been used.

    Attributes:
        status_code (int): The status code of the response (403 Forbidden).
        error (str): An error message explaining why access is forbidden.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_403_FORBIDDEN,
        read_only=True,
    )

    # Error message
    error = serializers.CharField(
        help_text=_("Error message explaining why access is forbidden."),
        read_only=True,
    )
