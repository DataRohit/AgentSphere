# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer


# User activation success response serializer
class UserActivationSuccessResponseSerializer(GenericResponseSerializer):
    """User activation success response serializer.

    This serializer defines the structure of the successful user activation response.
    It includes a status code and an activation object with a message.

    Attributes:
        status_code (int): The status code of the response.
        activation (UserActivationDataSerializer): The activation data.
    """

    # Nested serializer for the activation data
    class UserActivationDataSerializer(serializers.Serializer):
        """User Activation data serializer.

        This serializer defines the structure of the activation data.

        Attributes:
            message (str): A success message.
        """

        # Success message
        message = serializers.CharField(
            default=_("Account activated successfully"),
            help_text=_("Success message for account activation."),
            read_only=True,
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
    )

    # Activation data
    activation = UserActivationDataSerializer(
        help_text=_("Activation data containing success message."),
        read_only=True,
    )


# User activation forbidden response serializer
class UserActivationForbiddenResponseSerializer(GenericResponseSerializer):
    """User activation forbidden response serializer.

    This serializer defines the structure of the forbidden response for user activation
    when a token has expired or has already been used.

    Attributes:
        status_code (int): The status code of the response (403 Forbidden).
        error (str): An error message explaining why access is forbidden.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_403_FORBIDDEN,
        read_only=True,
    )

    # Error message
    error = serializers.CharField(
        help_text=_("Error message explaining why access is forbidden."),
        read_only=True,
    )
