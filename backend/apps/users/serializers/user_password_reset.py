# Third-party imports
from django.contrib.auth import get_user_model, password_validation
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer

# Get the user model
User = get_user_model()


# User password reset request serializer
class UserPasswordResetRequestSerializer(serializers.Serializer):
    """User password reset request serializer.

    This serializer handles requests to reset a user's password.
    It requires only the email address of the account.

    Attributes:
        email (str): The email address of the account.
    """

    # Email field
    email = serializers.EmailField(
        write_only=True,
        required=True,
        help_text=_("Email address of the account to reset password."),
        label=_("Email Address"),
    )

    # Validate the email
    def validate_email(self, value):
        """Validate the email address.

        Checks if the email belongs to an existing user.

        Args:
            value (str): The email address to validate.

        Returns:
            str: The validated email address.

        Raises:
            serializers.ValidationError: If no account with this email exists.
        """

        try:
            # Try to get the user by email
            User.objects.get(email=value)

        except User.DoesNotExist:
            # Raise a validation error if no account with this email exists
            raise serializers.ValidationError(
                _("No account with this email address exists."),
                code=status.HTTP_404_NOT_FOUND,
            ) from None

        # Return the validated email address
        return value


# User password reset request success response serializer
class UserPasswordResetRequestSuccessResponseSerializer(GenericResponseSerializer):
    """User password reset request success response serializer.

    This serializer defines the structure of the successful password reset request response.

    Attributes:
        status_code (int): The status code of the response.
        message (str): A success message.
    """

    # Nested serializer for the success message
    class UserPasswordResetRequestMessageSerializer(serializers.Serializer):
        """User password reset request message serializer.

        Attributes:
            message (str): A success message.
        """

        # Success message
        message = serializers.CharField(
            default=_("Password reset email sent successfully."),
            help_text=_("Success message for password reset request."),
            read_only=True,
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
    )

    # User field
    user = UserPasswordResetRequestMessageSerializer(
        help_text=_("Success message for password reset request."),
        read_only=True,
    )


# User password reset request unauthorized response serializer
class UserPasswordResetRequestUnauthorizedResponseSerializer(GenericResponseSerializer):
    """User password reset request unauthorized response serializer.

    This serializer defines the structure of the unauthorized error response for password reset request.

    Attributes:
        status_code (int): The HTTP status code.
        error (str): An error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_401_UNAUTHORIZED,
        read_only=True,
    )

    # Error message
    error = serializers.CharField(
        help_text=_("Error message for unauthorized password reset request."),
        read_only=True,
    )


# User password reset request error response serializer
class UserPasswordResetRequestErrorResponseSerializer(GenericResponseSerializer):
    """User password reset request error response serializer.

    This serializer defines the structure of the error response for password reset request.

    Attributes:
        status_code (int): The HTTP status code.
        errors (UserPasswordResetRequestErrorsSerializer): The validation errors.
    """

    # Nested serializer for validation errors
    class UserPasswordResetRequestErrorsSerializer(serializers.Serializer):
        """User password reset request errors serializer.

        Attributes:
            email (list): Errors related to the email field.
            non_field_errors (list): Non-field specific errors.
        """

        # Email field errors
        email = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the email field."),
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
        read_only=True,
    )

    # Errors
    errors = UserPasswordResetRequestErrorsSerializer(
        help_text=_("Object containing validation errors."),
    )


# User password reset confirm serializer
class UserPasswordResetConfirmSerializer(serializers.Serializer):
    """User password reset confirm serializer.

    This serializer handles the confirmation of password reset.
    It requires a new password and confirmation of the new password.

    Attributes:
        new_password (str): The new password for the account.
        re_new_password (str): Confirmation of the new password.
    """

    # New password field
    new_password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
        help_text=_("New password for account."),
        label=_("New Password"),
    )

    # Confirmation of new password field
    re_new_password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
        help_text=_("Confirm new password."),
        label=_("Confirm New Password"),
    )

    # Validate the passwords
    def validate(self, attrs):
        """Validate that passwords match and meet password requirements.

        Args:
            attrs (dict): The serializer attributes.

        Returns:
            dict: The validated attributes.

        Raises:
            serializers.ValidationError: If passwords don't match or fail validation.
        """

        # Check that the passwords match
        if attrs["new_password"] != attrs["re_new_password"]:
            # Raise a validation error if the passwords do not match
            raise serializers.ValidationError(
                {"re_new_password": _("Passwords do not match.")},
                code=status.HTTP_400_BAD_REQUEST,
            ) from None

        try:
            # Validate the password using Django's password validators
            password_validation.validate_password(attrs["new_password"])

        except Exception as e:
            # Raise a validation error if the password is not valid
            raise serializers.ValidationError(
                {"new_password": list(e)},
                code=status.HTTP_400_BAD_REQUEST,
            ) from e

        # Return the validated attributes
        return attrs


# User password reset confirm success response serializer
class UserPasswordResetConfirmSuccessResponseSerializer(GenericResponseSerializer):
    """User password reset confirm success response serializer.

    This serializer defines the structure of the successful password reset confirmation response.

    Attributes:
        status_code (int): The status code of the response.
        message (str): A success message.
    """

    # Nested serializer for the success message
    class UserPasswordResetConfirmMessageSerializer(serializers.Serializer):
        """User password reset confirm message serializer.

        Attributes:
            message (str): A success message.
        """

        # Success message
        message = serializers.CharField(
            default=_("Password reset successfully."),
            help_text=_("Success message for password reset."),
            read_only=True,
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
    )

    # User field
    user = UserPasswordResetConfirmMessageSerializer(
        help_text=_("Success message for password reset."),
        read_only=True,
    )


# User password reset confirm error response serializer
class UserPasswordResetConfirmErrorResponseSerializer(GenericResponseSerializer):
    """User password reset confirm error response serializer.

    This serializer defines the structure of the error response for password reset confirmation.

    Attributes:
        status_code (int): The HTTP status code.
        errors (UserPasswordResetConfirmErrorsSerializer): The validation errors.
    """

    # Nested serializer for validation errors
    class UserPasswordResetConfirmErrorsSerializer(serializers.Serializer):
        """User password reset confirm errors serializer.

        Attributes:
            new_password (list): Errors related to the new password field.
            re_new_password (list): Errors related to the confirmation password field.
            non_field_errors (list): Non-field specific errors.
        """

        # New password field errors
        new_password = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the new password field."),
        )

        # Confirmation password field errors
        re_new_password = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the confirmation password field."),
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
        read_only=True,
    )

    # Errors
    errors = UserPasswordResetConfirmErrorsSerializer(
        help_text=_("Object containing validation errors."),
    )


# User password reset forbidden response serializer
class UserPasswordResetForbiddenResponseSerializer(GenericResponseSerializer):
    """User password reset forbidden response serializer.

    This serializer defines the structure of the forbidden response for password reset
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
