# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Project imports
from apps.common.serializers import GenericResponseSerializer
from apps.organization.serializers.organization import OrganizationSerializer


# Organization list response serializer
class OrganizationListResponseSerializer(GenericResponseSerializer):
    """Organization list response serializer.

    This serializer defines the structure of the organization list response.
    It includes a status code and a list of organizations.

    Attributes:
        status_code (int): The status code of the response.
        organizations (List[OrganizationSerializer]): List of organization serializers.
    """

    # Status code
    status_code = serializers.IntegerField(default=status.HTTP_200_OK)

    # Organizations serializer
    organizations = OrganizationSerializer(
        many=True,
        read_only=True,
        help_text=_("List of organizations owned by the user."),
    )


# Organization membership list response serializer
class OrganizationMembershipListResponseSerializer(GenericResponseSerializer):
    """Organization membership list response serializer.

    This serializer defines the structure of the organization membership list response.
    It includes a status code and a list of organizations where the user is a member.

    Attributes:
        status_code (int): The status code of the response.
        organizations (List[OrganizationSerializer]): List of organization serializers.
    """

    # Status code
    status_code = serializers.IntegerField(default=status.HTTP_200_OK)

    # Organizations serializer
    organizations = OrganizationSerializer(
        many=True,
        read_only=True,
        help_text=_("List of organizations where the user is a member."),
    )
