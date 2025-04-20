# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer
from apps.conversation.serializers.session import SessionResponseSchema


# Session deactivate success response serializer
class SessionDeactivateSuccessResponseSerializer(GenericResponseSerializer):
    """Serializer for successful session deactivation response.

    This serializer defines the structure of the session deactivation success response.
    It includes a status code and the deactivated session details.

    Attributes:
        status_code (int): The status code of the response.
        session (SessionResponseSchema): The deactivated session details.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Session data
    session = SessionResponseSchema(
        help_text=_("The deactivated session details."),
        read_only=True,
    )


# Session not found error response serializer
class SessionDeactivateNotFoundResponseSerializer(GenericResponseSerializer):
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
class SessionDeactivateAuthErrorResponseSerializer(GenericResponseSerializer):
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
class SessionDeactivatePermissionDeniedResponseSerializer(GenericResponseSerializer):
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
        default=_("You do not have permission to deactivate this session."),
        read_only=True,
        help_text=_("Error message."),
    )
