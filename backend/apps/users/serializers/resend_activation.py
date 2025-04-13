# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Project imports
from apps.common.serializers import GenericResponseSerializer


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

    Defines the structure of the bad request error response (400 Bad Request).

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
            help_text=_("Non-field specific errors (e.g., already active)."),
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        help_text=_("HTTP status code indicating a bad request."),
    )

    # Errors - Point to the renamed nested serializer
    errors = ResendActivationErrorsDetailSerializer(
        help_text=_("Object containing error details."),
    )


# Resend activation not found response serializer
class ResendActivationNotFoundResponseSerializer(GenericResponseSerializer):
    """Resend activation not found response serializer (for schema).

    Defines the structure of the not found error response (404 Not Found).

    Attributes:
        status_code (int): The status code of the response.
        errors (ErrorsDetailSerializer): The errors detail serializer.
    """

    # Nested serializer defining the structure of the actual errors
    class ResendActivationNotFoundErrorsDetailSerializer(serializers.Serializer):
        """Resend Activation Not Found Errors detail serializer.

        Attributes:
            email (list): A list of errors related to the email field.
        """

        # Email field
        email = serializers.ListField(
            child=serializers.CharField(),
            default=["User with this email does not exist."],
            help_text=_("Errors related to the email field when user not found."),
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_404_NOT_FOUND,
        help_text=_("HTTP status code indicating resource not found."),
    )

    # Errors
    errors = ResendActivationNotFoundErrorsDetailSerializer(
        help_text=_("Object containing error details."),
    )
