# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Project imports
from apps.common.serializers import GenericResponseSerializer


# User deletion request success response serializer
class UserDeletionRequestSuccessResponseSerializer(GenericResponseSerializer):
    """User deletion request success response serializer.

    This serializer defines the structure of the successful deletion request response.

    Attributes:
        status_code (int): The status code of the response.
        message (str): A success message.
    """

    # Nested serializer for the success message
    class UserDeletionRequestMessageSerializer(serializers.Serializer):
        """User deletion request message serializer.

        Attributes:
            message (str): A success message.
        """

        # Success message
        message = serializers.CharField(
            default=_("Account deletion email sent successfully."),
            help_text=_("Success message for deletion request."),
            read_only=True,
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code indicating a successful request."),
    )

    # User field
    user = UserDeletionRequestMessageSerializer(
        help_text=_("Success message for deletion request."),
        read_only=True,
    )


# User deletion request unauthorized response serializer
class UserDeletionRequestUnauthorizedResponseSerializer(GenericResponseSerializer):
    """User deletion request unauthorized response serializer.

    This serializer defines the structure of the unauthorized error response for deletion request.

    Attributes:
        status_code (int): The HTTP status code.
        error (str): An error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_401_UNAUTHORIZED,
        read_only=True,
        help_text=_("HTTP status code indicating an unauthorized request."),
    )

    # Error message
    error = serializers.CharField(
        help_text=_("Error message for unauthorized deletion request."),
        read_only=True,
    )


# User deletion confirm success response serializer
class UserDeletionConfirmSuccessResponseSerializer(GenericResponseSerializer):
    """User deletion confirm success response serializer.

    This serializer defines the structure of the successful deletion confirmation response.

    Attributes:
        status_code (int): The status code of the response.
        message (str): A success message.
    """

    # Nested serializer for the success message
    class UserDeletionConfirmMessageSerializer(serializers.Serializer):
        """User deletion confirm message serializer.

        Attributes:
            message (str): A success message.
        """

        # Success message
        message = serializers.CharField(
            default=_("Account deleted successfully."),
            help_text=_("Success message for account deletion."),
            read_only=True,
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code indicating a successful request."),
    )

    # User field
    user = UserDeletionConfirmMessageSerializer(
        help_text=_("Success message for account deletion."),
        read_only=True,
    )


# User deletion forbidden response serializer
class UserDeletionForbiddenResponseSerializer(GenericResponseSerializer):
    """User deletion forbidden response serializer.

    This serializer defines the structure of the forbidden response for deletion
    when a token has expired or has already been used.

    Attributes:
        status_code (int): The status code of the response (403 Forbidden).
        error (str): An error message explaining why access is forbidden.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_403_FORBIDDEN,
        read_only=True,
        help_text=_("HTTP status code indicating a forbidden request."),
    )

    # Error message
    error = serializers.CharField(
        help_text=_("Error message explaining why access is forbidden."),
        read_only=True,
    )
