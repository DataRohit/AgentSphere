# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Project imports
from apps.common.serializers import GenericResponseSerializer
from apps.organization.serializers.organization import OrganizationSerializer


# Organization detail response serializer
class OrganizationDetailResponseSerializer(GenericResponseSerializer):
    """Organization detail response serializer.

    This serializer defines the structure of the organization detail response.
    It includes a status code and an organization object.

    Attributes:
        status_code (int): The status code of the response.
        organization (OrganizationSerializer): The organization detail serializer.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code indicating a successful request."),
    )

    # Organization serializer
    organization = OrganizationSerializer(
        read_only=True,
        help_text=_("The requested organization."),
    )


# Organization not found response serializer
class OrganizationNotFoundResponseSerializer(GenericResponseSerializer):
    """Organization not found response serializer.

    This serializer defines the structure of the not found response
    when the organization doesn't exist or user doesn't have permission.

    Attributes:
        status_code (int): The status code of the response (404 Not Found).
        error (str): An error message explaining why the resource was not found.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_404_NOT_FOUND,
        read_only=True,
        help_text=_("HTTP status code indicating a not found resource."),
    )

    # Error message
    error = serializers.CharField(
        default=_("Organization not found or you do not have permission."),
        read_only=True,
        help_text=_("Error message explaining why the resource was not found."),
    )
