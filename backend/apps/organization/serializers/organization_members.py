# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer
from apps.users.serializers import UserDetailSerializer


# Organization members list response serializer
class OrganizationMembersListResponseSerializer(GenericResponseSerializer):
    """Organization members list response serializer.

    This serializer defines the structure of the organization members list response.
    It includes a status code and a list of users who are members of the organization.

    Attributes:
        status_code (int): The status code of the response.
        members (List[UserDetailSerializer]): List of user detail serializers.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code indicating a successful request."),
    )

    # Members serializer
    members = UserDetailSerializer(
        many=True,
        read_only=True,
        help_text=_("List of users who are members of the organization."),
    )


# Organization access forbidden response serializer
class OrganizationNotOwnerResponseSerializer(GenericResponseSerializer):
    """Organization access forbidden response serializer.

    This serializer defines the structure of the response when a user tries to
    access an organization they don't have permission to access.

    Attributes:
        status_code (int): The status code of the response.
        error (str): An error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_403_FORBIDDEN,
        read_only=True,
        help_text=_("HTTP status code indicating a forbidden request."),
    )

    # Error message
    error = serializers.CharField(
        default=_("You must be the owner or a member of this organization to view its members."),
        read_only=True,
        help_text=_("Error message explaining why access is forbidden."),
    )
