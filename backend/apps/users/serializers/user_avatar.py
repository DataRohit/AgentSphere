# Third-party imports
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from PIL import ImageFile
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer
from apps.users.serializers.user_profile import UserProfileSerializer

# Get the User model
User = get_user_model()


# User avatar upload serializer
class UserAvatarSerializer(serializers.Serializer):
    """User avatar upload serializer.

    This serializer handles uploading an avatar image for a user.
    It validates that the file is an image in jpg, jpeg, or png format.

    Attributes:
        avatar (ImageField): The avatar image file.
    """

    # Avatar image field
    avatar = serializers.ImageField(
        help_text=_("Avatar image file (jpg, jpeg, or png)."),
        required=True,
    )

    # Validate the file type
    def validate_avatar(self, value: ImageFile) -> ImageFile:
        """Validate the avatar file.

        Args:
            value (ImageFile): The avatar file to validate.

        Returns:
            ImageFile: The validated avatar file.

        Raises:
            serializers.ValidationError: If the file is not a valid image type.
        """

        # Get the file extension
        file_extension = value.name.split(".")[-1].lower()

        # Check if the file is a valid image type
        if file_extension not in ["jpg", "jpeg", "png"]:
            # Raise a validation error if the file is not a valid image type
            raise serializers.ValidationError(
                _("Only jpg, jpeg, and png files are allowed."),
                code=status.HTTP_400_BAD_REQUEST,
            )

        # Return the validated file
        return value


# User avatar success response serializer
class UserAvatarSuccessResponseSerializer(GenericResponseSerializer):
    """User avatar success response serializer.

    This serializer defines the structure of the successful avatar upload response.

    Attributes:
        status_code (int): The status code of the response.
        user (UserProfileSerializer): The updated user profile data.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_200_OK,
        read_only=True,
    )

    # User profile
    user = UserProfileSerializer(
        help_text=_("Updated user profile data with avatar URL."),
        read_only=True,
    )


# User avatar error response serializer
class UserAvatarErrorResponseSerializer(GenericResponseSerializer):
    """User avatar error response serializer.

    This serializer defines the structure of the avatar upload error response.

    Attributes:
        status_code (int): The HTTP status code.
        errors (UserAvatarErrorsSerializer): The validation errors.
    """

    # Nested serializer for validation errors
    class UserAvatarErrorsSerializer(serializers.Serializer):
        """User avatar errors serializer.

        Attributes:
            avatar (list): Errors related to the avatar field.
            non_field_errors (list): Non-field specific errors.
        """

        # Avatar field errors
        avatar = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the avatar field."),
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
        help_text=_("HTTP status code indicating validation errors."),
        read_only=True,
    )

    # Errors
    errors = UserAvatarErrorsSerializer(
        help_text=_("Object containing validation errors."),
    )


# User avatar auth error response serializer
class UserAvatarAuthErrorResponseSerializer(GenericResponseSerializer):
    """User avatar auth error response serializer.

    This serializer defines the structure of the authentication error response.

    Attributes:
        status_code (int): The HTTP status code.
        error (str): The error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_401_UNAUTHORIZED,
        read_only=True,
        help_text=_("HTTP status code indicating an authentication error."),
    )

    # Error message field
    error = serializers.CharField(
        help_text=_("Authentication error message."),
        read_only=True,
    )
