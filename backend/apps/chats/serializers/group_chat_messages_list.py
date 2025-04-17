# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.chats.serializers.message import MessageResponseSchema
from apps.common.serializers import GenericResponseSerializer


# Group chat messages list success response serializer
class GroupChatMessagesListSuccessResponseSerializer(GenericResponseSerializer):
    """Group chat messages list success response serializer.

    This serializer defines the structure of the group chat messages list success response.
    It includes a status code and a list of messages.

    Attributes:
        status_code (int): The status code of the response (200 OK).
        messages (list): A list of messages in the group chat.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Messages list
    messages = MessageResponseSchema(
        many=True,
        read_only=True,
        help_text=_("List of messages in the group chat."),
    )


# Group chat messages list missing parameter response serializer
class GroupChatMessagesListMissingParamResponseSerializer(GenericResponseSerializer):
    """Group chat messages list missing parameter response serializer.

    This serializer defines the structure of the missing parameter error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response (400 Bad Request).
        error (str): An error message explaining the missing parameter.
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


# Group chat messages list authentication error response serializer
class GroupChatMessagesListAuthErrorResponseSerializer(GenericResponseSerializer):
    """Group chat messages list authentication error response serializer.

    This serializer defines the structure of the authentication error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response (401 Unauthorized).
        error (str): An error message explaining the authentication error.
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


# Group chat messages list not found response serializer
class GroupChatMessagesListNotFoundResponseSerializer(GenericResponseSerializer):
    """Group chat messages list not found response serializer.

    This serializer defines the structure of the not found error response.
    It includes a status code and an error message.
    Used for both chat not found and no messages found scenarios.

    Attributes:
        status_code (int): The status code of the response (404 Not Found).
        error (str): An error message explaining that the chat or messages were not found.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_404_NOT_FOUND,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("Resource not found."),
        read_only=True,
        help_text=_("Error message. Could be 'Group chat not found.' or 'No messages found in this chat.'"),
    )


# Group chat messages list permission denied response serializer
class GroupChatMessagesListPermissionDeniedResponseSerializer(GenericResponseSerializer):
    """Group chat messages list permission denied response serializer.

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
        default=_("You do not have permission to view messages in this chat."),
        read_only=True,
        help_text=_("Error message."),
    )
