# Standard library imports
from typing import Any

# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# User login serializer (extends TokenObtainPairSerializer)
class UserLoginSerializer(TokenObtainPairSerializer):
    """User login serializer.

    This serializer handles user authentication and generates JWT tokens.
    It extends the TokenObtainPairSerializer to provide customized token claims.

    Attributes:
        email (str): The user's email address for authentication.
        password (str): The user's password for authentication.

    Meta:
        fields (list): The fields to include in the serializer.
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

    # Meta class for the UserLoginSerializer
    class Meta:
        """Meta class for the UserLoginSerializer.

        This class defines the fields to include in the serializer.

        Attributes:
            fields (list): The fields to include in the serializer.
        """

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
