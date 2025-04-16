# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.chats.serializers.group_chat import GroupChatResponseSchema
from apps.common.serializers import GenericResponseSerializer


# GroupChat detail success response serializer
class GroupChatDetailSuccessResponseSerializer(GenericResponseSerializer):
    """GroupChat detail success response serializer.

    This serializer defines the structure of the group chat detail success response.
    It includes a status code and a group chat object.

    Attributes:
        status_code (int): The status code of the response.
        group_chat (GroupChatResponseSchema): The group chat with detailed information.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Chat data
    chat = GroupChatResponseSchema(
        help_text=_(
            "The chat with detailed organization, user, and agents information.",
        ),
    )


# GroupChat detail not found response serializer
class GroupChatDetailNotFoundResponseSerializer(GenericResponseSerializer):
    """GroupChat detail not found response serializer.

    This serializer defines the structure of the group chat detail not found response.
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
        default=_("Group chat not found."),
        read_only=True,
        help_text=_("Error message for the response."),
    )


# GroupChat detail permission denied response serializer
class GroupChatDetailPermissionDeniedResponseSerializer(GenericResponseSerializer):
    """GroupChat detail permission denied response serializer.

    This serializer defines the structure of the group chat detail permission denied response.
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
        default=_("You do not have permission to view this chat."),
        read_only=True,
        help_text=_("Error message for the response."),
    )


# GroupChat detail auth error response serializer
class GroupChatDetailAuthErrorResponseSerializer(GenericResponseSerializer):
    """GroupChat detail auth error response serializer.

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
        help_text=_("Error message for the response."),
    )
