# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Project imports
from apps.common.serializers import GenericResponseSerializer


# Organization authentication error response serializer
class OrganizationAuthErrorResponseSerializer(GenericResponseSerializer):
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
    )

    # Error message
    error = serializers.CharField(
        default=_("Authentication credentials were not provided or are invalid."),
        read_only=True,
        help_text=_("Error message explaining the authentication failure."),
    )
