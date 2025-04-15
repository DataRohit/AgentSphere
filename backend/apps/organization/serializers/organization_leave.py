# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer


# Organization leave success response serializer
class OrganizationLeaveSuccessResponseSerializer(GenericResponseSerializer):
    """Organization leave success response serializer.

    This serializer defines the structure of the successful organization leave response.
    It includes a status code and a success message.

    Attributes:
        status_code (int): The status code of the response.
        message (str): A success message.
    """

    # Organization leave success message response serializer
    class OrganizationLeaveSuccessMessageResponseSerializer(serializers.Serializer):
        """Organization leave success message response serializer.

        Attributes:
            message (str): A success message.
        """

        # Message
        message = serializers.CharField(
            default=_("You have successfully left the organization."),
            read_only=True,
            help_text=_(
                "Success message confirming the user has left the organization.",
            ),
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
        help_text=_("HTTP status code indicating a successful request."),
    )

    # Success message
    organization = OrganizationLeaveSuccessMessageResponseSerializer(
        read_only=True,
        help_text=_("Success message confirming the user has left the organization."),
    )


# Organization leave error response serializer
class OrganizationLeaveErrorResponseSerializer(GenericResponseSerializer):
    """Organization leave error response serializer.

    This serializer defines the structure of the error response for the leave operation.

    Attributes:
        status_code (int): The status code of the response.
        errors (OrganizationLeaveErrorsDetailSerializer): The errors detail serializer.
    """

    # Nested serializer defining the structure of the actual errors
    class OrganizationLeaveErrorsDetailSerializer(serializers.Serializer):
        """Organization Leave Errors detail serializer.

        Attributes:
            non_field_errors (list): Non-field specific errors.
        """

        # Non-field errors
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Non-field specific errors."),
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code indicating a bad request."),
    )

    # Errors
    errors = OrganizationLeaveErrorsDetailSerializer(
        help_text=_("Object containing validation errors."),
        read_only=True,
    )


# Organization not a member error response serializer
class OrganizationNotMemberResponseSerializer(GenericResponseSerializer):
    """Organization not a member error response serializer.

    This serializer defines the structure of the error response when a user
    tries to leave an organization they are not a member of.

    Attributes:
        status_code (int): The status code of the response.
        error (str): The error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_403_FORBIDDEN,
        read_only=True,
        help_text=_("HTTP status code indicating forbidden access."),
    )

    # Error message
    error = serializers.CharField(
        default=_("You are not a member of this organization."),
        read_only=True,
        help_text=_("Error message."),
    )
