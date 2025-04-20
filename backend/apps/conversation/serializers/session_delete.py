# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer


# Session delete success response serializer
class SessionDeleteSuccessResponseSerializer(GenericResponseSerializer):
    """Serializer for successful session deletion response.

    This serializer defines the structure of the session deletion success response.
    It includes a status code and a success message.

    Attributes:
        status_code (int): The status code of the response.
        message (str): A success message.
    """

    # Session delete success message response serializer
    class SessionDeleteSuccessMessageResponseSerializer(serializers.Serializer):
        """Session delete success message response serializer.

        Attributes:
            message (str): A success message.
        """

        # Message
        message = serializers.CharField(
            default=_("Session deleted successfully."),
            read_only=True,
            help_text=_("Success message confirming the session was deleted."),
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Success message
    session = SessionDeleteSuccessMessageResponseSerializer(
        read_only=True,
        help_text=_("Success message confirming the session was deleted."),
    )


# Session not found error response serializer
class SessionDeleteNotFoundResponseSerializer(GenericResponseSerializer):
    """Serializer for session not found error response.

    This serializer defines the structure of the not found error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response.
        error (str): The error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_404_NOT_FOUND,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("Session not found."),
        read_only=True,
        help_text=_("Error message."),
    )


# Session auth error response serializer
class SessionDeleteAuthErrorResponseSerializer(GenericResponseSerializer):
    """Serializer for session authentication error response.

    This serializer defines the structure of the authentication error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response.
        error (str): The error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_401_UNAUTHORIZED,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("Authentication credentials were not provided."),
        read_only=True,
        help_text=_("Error message."),
    )


# Session permission denied response serializer
class SessionDeletePermissionDeniedResponseSerializer(GenericResponseSerializer):
    """Serializer for session permission denied response.

    This serializer defines the structure of the permission denied error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response.
        error (str): The error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_403_FORBIDDEN,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("You do not have permission to delete this session."),
        read_only=True,
        help_text=_("Error message."),
    )
