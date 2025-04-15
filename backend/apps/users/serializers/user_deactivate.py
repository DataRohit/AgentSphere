# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer


# User deactivate serializer
class UserDeactivateSerializer(serializers.Serializer):
    """User deactivate serializer.

    This serializer handles deactivating a user's account.
    It requires the current password to be entered twice for confirmation.

    Attributes:
        current_password (str): The user's current password.
        re_password (str): Confirmation of the user's current password.
    """

    # Current password field
    current_password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
        help_text=_("Current password for account deactivation verification."),
        label=_("Current Password"),
    )

    # Confirmation password field
    re_password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
        help_text=_("Confirm current password."),
        label=_("Confirm Password"),
    )

    # Validate the passwords match and are correct
    def validate(self, attrs):
        """Validate that passwords match and the current password is correct.

        Args:
            attrs (dict): The serializer attributes.

        Returns:
            dict: The validated attributes.

        Raises:
            serializers.ValidationError: If passwords don't match or current password is incorrect.
        """

        # Check that the passwords match
        if attrs["current_password"] != attrs["re_password"]:
            # Raise a validation error if the passwords don't match
            raise serializers.ValidationError(
                {"re_password": _("Passwords do not match.")},
                code=status.HTTP_400_BAD_REQUEST,
            ) from None

        # Get the user from the context
        user = self.context["request"].user

        # Check if the current password is correct
        if not user.check_password(attrs["current_password"]):
            # Raise a validation error if the current password is incorrect
            raise serializers.ValidationError(
                {"current_password": _("Current password is incorrect.")},
                code=status.HTTP_400_BAD_REQUEST,
            ) from None

        # Return the validated attributes
        return attrs


# User deactivate success response serializer
class UserDeactivateSuccessResponseSerializer(GenericResponseSerializer):
    """User deactivate success response serializer.

    This serializer defines the structure of the successful account deactivation response.

    Attributes:
        status_code (int): The status code of the response.
        message (str): A success message.
    """

    # Nested serializer for the success message
    class UserDeactivateMessageSerializer(serializers.Serializer):
        """User deactivate message serializer.

        Attributes:
            message (str): A success message.
        """

        # Success message
        message = serializers.CharField(
            default=_("Account deactivated successfully."),
            help_text=_("Success message for account deactivation."),
            read_only=True,
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
    )

    # User field
    user = UserDeactivateMessageSerializer(
        help_text=_("Success message for account deactivation."),
        read_only=True,
    )


# User deactivate error response serializer
class UserDeactivateErrorResponseSerializer(GenericResponseSerializer):
    """User deactivate error response serializer.

    This serializer defines the structure of the error response for account deactivation.

    Attributes:
        status_code (int): The HTTP status code.
        errors (UserDeactivateErrorsSerializer): The validation errors.
    """

    # Nested serializer for validation errors
    class UserDeactivateErrorsSerializer(serializers.Serializer):
        """User deactivate errors serializer.

        Attributes:
            current_password (list): Errors related to the current password field.
            re_password (list): Errors related to the confirmation password field.
            non_field_errors (list): Non-field specific errors.
        """

        # Current password field errors
        current_password = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the current password field."),
        )

        # Confirmation password field errors
        re_password = serializers.ListField(
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
    errors = UserDeactivateErrorsSerializer(
        help_text=_("Object containing validation errors."),
    )
