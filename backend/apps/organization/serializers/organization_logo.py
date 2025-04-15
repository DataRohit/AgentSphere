# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer
from apps.organization.serializers.organization import OrganizationSerializer


# Organization logo serializer
class OrganizationLogoSerializer(serializers.Serializer):
    """Organization logo upload serializer.

    This serializer handles the upload of organization logos.
    It validates that the file is a valid image (jpg/jpeg/png).

    Attributes:
        logo (ImageField): The logo file to upload.
    """

    # Logo field
    logo = serializers.ImageField(
        help_text=_("The organization logo file to upload (jpg/jpeg/png)."),
    )

    # Validate the logo field
    def validate_logo(self, value):
        """Validate the logo field.

        This method validates that the file is a valid image (jpg/jpeg/png).

        Args:
            value (InMemoryUploadedFile): The uploaded file.

        Returns:
            InMemoryUploadedFile: The validated file.

        Raises:
            serializers.ValidationError: If the file is not a valid image.
            serializers.ValidationError: If the file is too large (>2MB).
        """

        # Get the content type
        content_type = value.content_type

        # Check if the file is a valid image
        if content_type not in ["image/jpeg", "image/jpg", "image/png"]:
            # Raise a validation error
            raise serializers.ValidationError(
                [
                    "Invalid image format. Please upload a valid image file (jpg/jpeg/png).",
                ],
            ) from None

        # Get the file size (in bytes)
        file_size = value.size

        # Check if the file is too large (2MB)
        if file_size > 2 * 1024 * 1024:
            # Raise a validation error
            raise serializers.ValidationError(
                [
                    "Image file too large. Please upload a file smaller than 2MB.",
                ],
            ) from None

        # Return the value
        return value


# Organization logo success response serializer
class OrganizationLogoSuccessResponseSerializer(GenericResponseSerializer):
    """Organization logo upload success response serializer.

    This serializer defines the structure of the successful logo upload response.
    It includes a status code and the updated organization object.

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
        help_text=_("The updated organization with new logo URL."),
    )


# Organization logo error response serializer
class OrganizationLogoErrorResponseSerializer(GenericResponseSerializer):
    """Organization logo upload error response serializer.

    This serializer defines the structure of the error response for logo upload.

    Attributes:
        status_code (int): The status code of the response.
        errors (OrganizationLogoErrorsDetailSerializer): The errors detail serializer.
    """

    # Nested serializer defining the structure of the actual errors
    class OrganizationLogoErrorsDetailSerializer(serializers.Serializer):
        """Organization Logo Errors detail serializer.

        Attributes:
            logo (list): Errors related to the logo field.
            non_field_errors (list): Non-field specific errors.
        """

        # Logo field errors
        logo = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the logo field."),
        )

        # Non-field errors
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Non-field specific errors."),
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        help_text=_("HTTP status code indicating a bad request."),
        read_only=True,
    )

    # Errors
    errors = OrganizationLogoErrorsDetailSerializer(
        help_text=_("Object containing validation errors."),
        read_only=True,
    )


# Organization logo not found response serializer
class OrganizationLogoNotFoundResponseSerializer(GenericResponseSerializer):
    """Organization logo not found response serializer.

    This serializer defines the structure of the not found response for logo upload
    when the organization doesn't exist or the user is not the owner.

    Attributes:
        status_code (int): The status code of the response (404 Not Found).
        error (str): An error message explaining why the resource was not found.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_404_NOT_FOUND,
        read_only=True,
    )

    # Error message
    error = serializers.CharField(
        default=_("Organization not found or you do not have permission."),
        read_only=True,
        help_text=_("Error message explaining why the resource was not found."),
    )
