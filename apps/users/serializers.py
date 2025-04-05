# Standard library imports
from typing import Any

# Third-party imports
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

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
        errors (UserCreateErrorsDetailSerializer): The errors detail serializer.
    """

    # Nested serializer defining the structure of the actual errors
    class UserCreateErrorsDetailSerializer(serializers.Serializer):
        """User Creation Errors detail serializer.

        Attributes:
            username (list): Errors related to the username field.
            email (list): Errors related to the email field.
            first_name (list): Errors related to the first name field.
            last_name (list): Errors related to the last name field.
            password (list): Errors related to the password field.
            re_password (list): Errors related to the password confirmation field.
            non_field_errors (list): Non-field specific errors.
        """

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
    errors = UserCreateErrorsDetailSerializer(
        help_text=_("Object containing validation errors."),
    )


# User activation success response serializer
class UserActivationSuccessResponseSerializer(GenericResponseSerializer):
    """User activation success response serializer.

    This serializer defines the structure of the successful user activation response.
    It includes a status code and an activation object with a message.

    Attributes:
        status_code (int): The status code of the response.
        activation (UserActivationDataSerializer): The activation data.
    """

    # Nested serializer for the activation data
    class UserActivationDataSerializer(serializers.Serializer):
        """User Activation data serializer.

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
    activation = UserActivationDataSerializer(
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


# Resend activation email serializer
class ResendActivationEmailSerializer(serializers.Serializer):
    """Serializer for requesting a resend of the activation email.

    Requires the user's email address to identify the account.

    Attributes:
        email (str): The user's email address.
    """

    # Email field
    email = serializers.EmailField(
        write_only=True,
        help_text=_("Email address of the user needing a new activation link."),
        label=_("Email Address"),
    )


# Resend activation success response serializer
class ResendActivationSuccessResponseSerializer(GenericResponseSerializer):
    """Resend activation success response serializer.

    Defines the structure of the successful resend activation response.

    Attributes:
        status_code (int): The status code of the response.
        activation (ResendActivationDataSerializer): The activation data.
    """

    # Nested serializer for the activation data
    class ResendActivationDataSerializer(serializers.Serializer):
        """Resend Activation data serializer.

        Attributes:
            message (str): A success message.
        """

        # Success message
        message = serializers.CharField(
            default=_("Activation email resent successfully."),
            help_text=_("Success message for resending activation email."),
            read_only=True,
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
    )

    # Activation data
    activation = ResendActivationDataSerializer(read_only=True)


# Resend activation error response serializer
class ResendActivationErrorResponseSerializer(GenericResponseSerializer):
    """Resend activation error response serializer (for schema).

    Defines the structure of the error response (e.g., 400 Bad Request, 404 Not Found).

    Attributes:
        status_code (int): The status code of the response.
        errors (ErrorsDetailSerializer): The errors detail serializer.
    """

    # Nested serializer defining the structure of the actual errors
    class ResendActivationErrorsDetailSerializer(serializers.Serializer):
        """Resend Activation Errors detail serializer.

        Attributes:
            email (list): A list of errors related to the email field.
            non_field_errors (list): A list of non-field specific errors.
        """

        # Email field
        email = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the email field."),
        )

        # Non-field errors
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=(
                _("Non-field specific errors (e.g., user not found, already active).")
            ),
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        help_text=_("HTTP status code indicating the error."),
    )

    # Errors - Point to the renamed nested serializer
    errors = ResendActivationErrorsDetailSerializer(
        help_text=_("Object containing error details."),
    )


# User login serializer (extends TokenObtainPairSerializer)
class UserLoginSerializer(TokenObtainPairSerializer):
    """User login serializer.

    This serializer handles user authentication and generates JWT tokens.
    It extends the TokenObtainPairSerializer to provide customized token claims.

    Attributes:
        email (str): The user's email address for authentication.
        password (str): The user's password for authentication.
    """

    # Email field for authentication
    email = serializers.EmailField(
        help_text=_("User's email address for authentication."),
        label=_("Email Address"),
    )

    # Override password field to add better documentation
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text=_("User's password for authentication."),
        label=_("Password"),
    )

    # No username field as we use email authentication
    username = None

    # Meta class
    class Meta:
        # Fields to include in the serializer
        fields = ["email", "password"]

    # Override the validate method to use email for authentication
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate the login credentials.

        This method validates the email and password provided for authentication.

        Args:
            attrs (dict[str, Any]): The attributes to validate.

        Returns:
            dict[str, Any]: The validated attributes.

        Raises:
            serializers.ValidationError: If authentication fails.
        """

        # Set the username field to the email field for JWT validation
        attrs[self.username_field] = attrs.get("email")

        # Call the parent validate method
        return super().validate(attrs)

    # Override the get_token method to add custom claims
    @classmethod
    def get_token(cls, user):
        """Get token for the user with custom claims.

        This method generates a token for the user and adds custom claims.

        Args:
            user (User): The user for whom to generate the token.

        Returns:
            Token: The generated token.
        """

        # Get the token
        token = super().get_token(user)

        # Add custom claims
        token["email"] = user.email
        token["full_name"] = user.full_name
        token["is_staff"] = user.is_staff
        token["is_superuser"] = user.is_superuser

        # Return the token
        return token


# User login response serializer
class UserLoginResponseSerializer(serializers.Serializer):
    """User login response serializer.

    This serializer defines the structure of the login response.

    Attributes:
        refresh (str): The refresh token for obtaining new access tokens.
        access (str): The access token for authenticating API requests.
    """

    # Refresh token field
    refresh = serializers.CharField(
        help_text=_("Refresh token for obtaining new access tokens."),
        read_only=True,
    )

    # Access token field
    access = serializers.CharField(
        help_text=_("Access token for authenticating API requests."),
        read_only=True,
    )


# User login error response serializer
class UserLoginErrorResponseSerializer(serializers.Serializer):
    """User login error response serializer.

    This serializer defines the structure of the login error response.

    Attributes:
        error (str): The error message.
    """

    # Error message field
    error = serializers.CharField(
        help_text=_("Error message for login failure."),
        read_only=True,
    )


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
            "is_active": {"read_only": True},
            "is_staff": {"read_only": True},
            "is_superuser": {"read_only": True},
            "date_joined": {"read_only": True},
            "last_login": {"read_only": True},
        }


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
