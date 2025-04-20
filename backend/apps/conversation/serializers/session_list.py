# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer
from apps.conversation.serializers.session import SessionResponseSchema


# Session list success response serializer
class SessionListSuccessResponseSerializer(GenericResponseSerializer):
    """Serializer for successful session list response.

    This serializer defines the structure of the session list success response.
    It includes a status code and a list of sessions.

    Attributes:
        status_code (int): The status code of the response.
        sessions (list): A list of sessions.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Sessions list
    sessions = SessionResponseSchema(
        many=True,
        read_only=True,
        help_text=_("List of active sessions."),
    )


# Session count success response serializer
class SessionCountSuccessResponseSerializer(GenericResponseSerializer):
    """Serializer for successful session count response.

    This serializer defines the structure of the session count success response.
    It includes a status code and a count of sessions.

    Attributes:
        status_code (int): The status code of the response.
        sessions (dict): A dictionary containing the count of sessions.
    """

    # Session count success message response serializer
    class SessionCountSuccessMessageResponseSerializer(serializers.Serializer):
        """Session count success message response serializer.

        Attributes:
            count (int): The count of active sessions.
        """

        # Count
        count = serializers.IntegerField(
            read_only=True,
            help_text=_("Count of active sessions."),
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Sessions count
    sessions = SessionCountSuccessMessageResponseSerializer(
        read_only=True,
        help_text=_("Count of active sessions."),
    )


# Session list auth error response serializer
class SessionListAuthErrorResponseSerializer(GenericResponseSerializer):
    """Serializer for session list authentication error response.

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


# Session list permission denied response serializer
class SessionListPermissionDeniedResponseSerializer(GenericResponseSerializer):
    """Serializer for session list permission denied response.

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
        default=_("You do not have permission to view these sessions."),
        read_only=True,
        help_text=_("Error message."),
    )


# Session list missing param response serializer
class SessionListMissingParamResponseSerializer(GenericResponseSerializer):
    """Serializer for session list missing parameter response.

    This serializer defines the structure of the missing parameter error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response.
        error (str): The error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("Missing required parameter."),
        read_only=True,
        help_text=_("Error message."),
    )
