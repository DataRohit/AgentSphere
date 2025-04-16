# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer


# SingleChat delete success response serializer
class SingleChatDeleteSuccessResponseSerializer(GenericResponseSerializer):
    """SingleChat delete success response serializer.

    This serializer defines the structure of the single chat delete success response.
    It includes a status code and a nested message object.

    Attributes:
        status_code (int): The status code of the response (200 OK).
        chat (SingleChatDeleteMessageResponseSerializer): A nested serializer containing the success message.
    """

    # SingleChat delete message response serializer
    class SingleChatDeleteMessageResponseSerializer(serializers.Serializer):
        """SingleChat delete message response serializer.

        Attributes:
            message (str): A success message confirming the chat was deleted.
        """

        # Message
        message = serializers.CharField(
            default=_("Chat deleted successfully."),
            read_only=True,
            help_text=_("Message confirming the chat was deleted."),
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Success message nested in chat object
    chat = SingleChatDeleteMessageResponseSerializer(
        read_only=True,
        help_text=_("Object containing the success message."),
    )


# SingleChat delete not found response serializer
class SingleChatDeleteNotFoundResponseSerializer(GenericResponseSerializer):
    """SingleChat delete not found response serializer.

    This serializer defines the structure of the not found error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response (404 Not Found).
        error (str): An error message explaining that the chat was not found.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_404_NOT_FOUND,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("Chat not found."),
        read_only=True,
        help_text=_("Error message explaining that the chat was not found."),
    )


# SingleChat delete permission denied response serializer
class SingleChatDeletePermissionDeniedResponseSerializer(GenericResponseSerializer):
    """SingleChat delete permission denied response serializer.

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
        default=_("You do not have permission to delete this chat."),
        read_only=True,
        help_text=_("Error message explaining the permission denial."),
    )


# Authentication error response serializer
class SingleChatDeleteAuthErrorResponseSerializer(GenericResponseSerializer):
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
