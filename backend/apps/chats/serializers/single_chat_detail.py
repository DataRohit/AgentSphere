# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.chats.serializers.single_chat import SingleChatResponseSchema
from apps.common.serializers import GenericResponseSerializer


# SingleChat detail success response serializer
class SingleChatDetailSuccessResponseSerializer(GenericResponseSerializer):
    """SingleChat detail success response serializer.

    This serializer defines the structure of the single chat detail success response.
    It includes a status code and a single chat object.

    Attributes:
        status_code (int): The status code of the response.
        single_chat (SingleChatResponseSchema): The single chat with detailed information.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Chat data
    chat = SingleChatResponseSchema(
        help_text=_(
            "The chat with detailed organization, user, and agent information.",
        ),
    )


# SingleChat not found error response serializer
class SingleChatDetailNotFoundResponseSerializer(GenericResponseSerializer):
    """SingleChat not found error response serializer.

    This serializer defines the structure of the single chat not found error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response (404 Not Found).
        error (str): An error message explaining that the single chat was not found.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_404_NOT_FOUND,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("Single chat not found."),
        read_only=True,
        help_text=_("Error message explaining that the single chat was not found."),
    )


# SingleChat permission denied error response serializer
class SingleChatDetailPermissionDeniedResponseSerializer(GenericResponseSerializer):
    """Permission denied error response serializer.

    This serializer defines the structure of the permission denied error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response (403 Forbidden).
        error (str): An error message explaining the permission denial.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_403_FORBIDDEN,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("You do not have permission to view this chat."),
        read_only=True,
        help_text=_("Error message explaining the permission denial."),
    )


# Authentication error response serializer
class SingleChatDetailAuthErrorResponseSerializer(GenericResponseSerializer):
    """Authentication error response serializer.

    This serializer defines the structure of the authentication error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response (401 Unauthorized).
        error (str): An error message explaining the authentication failure.
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
        help_text=_("Error message explaining the authentication failure."),
    )
