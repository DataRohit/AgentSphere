# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


# Generic Response Serializer
class GenericResponseSerializer(serializers.Serializer):
    """Serializer for Generic API responses.

    This serializer provides a standardized structure for Generic API responses,
    including a status code and a data payload.

    Attributes:
        status_code (int): HTTP status code for the response.
    """

    # Status code for the response
    status_code = serializers.IntegerField(
        default=200,
        help_text=_("HTTP status code for the response"),
    )
