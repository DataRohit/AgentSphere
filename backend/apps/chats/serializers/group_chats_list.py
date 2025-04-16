# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.chats.serializers.group_chat import GroupChatResponseSchema
from apps.common.serializers import GenericResponseSerializer


# Group chats list success response serializer
class GroupChatsListSuccessResponseSerializer(GenericResponseSerializer):
    """Group chats list success response serializer.

    This serializer defines the structure of the group chats list success response.
    It includes a status code and a list of chats.

    Attributes:
        status_code (int): The status code of the response (200 OK).
        chats (list): A list of group chats in the organization.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Chats list
    chats = GroupChatResponseSchema(
        many=True,
        read_only=True,
        help_text=_("List of group chats in the organization."),
    )


# Group chats list missing parameter response serializer
class GroupChatsListMissingParamResponseSerializer(GenericResponseSerializer):
    """Group chats list missing parameter response serializer.

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
        default="Missing required parameter: organization_id",
        read_only=True,
        help_text=_("Error message."),
    )


# Group chats list permission denied response serializer
class GroupChatsListPermissionDeniedResponseSerializer(GenericResponseSerializer):
    """Group chats list permission denied response serializer.

    This serializer defines the structure of the permission denied error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response (403 Forbidden).
        error (str): An error message explaining the permission denied error.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_403_FORBIDDEN,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default="You are not a member of this organization.",
        read_only=True,
        help_text=_("Error message."),
    )


# Group chats list authentication error response serializer
class GroupChatsListAuthErrorResponseSerializer(GenericResponseSerializer):
    """Group chats list authentication error response serializer.

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
        default="Authentication credentials were not provided.",
        read_only=True,
        help_text=_("Error message."),
    )


# Group chats list not found response serializer
class GroupChatsListNotFoundResponseSerializer(GenericResponseSerializer):
    """Group chats list not found response serializer.

    This serializer defines the structure of the not found error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response (404 Not Found).
        error (str): An error message explaining that no chats were found.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_404_NOT_FOUND,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default="No group chats found matching the criteria.",
        read_only=True,
        help_text=_("Error message."),
    )
