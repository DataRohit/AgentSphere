# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework import status

# Project imports
from apps.common.serializer import GenericResponseSerializer
from apps.organization.models import Organization
from apps.users.serializers import UserDetailSerializer


# Organization serializer
class OrganizationSerializer(serializers.ModelSerializer):
    """Organization serializer.

    This serializer provides a representation of the Organization model.

    Attributes:
        id (UUID): The organization's ID.
        name (str): The organization's name.
        description (str): The organization's description.
        website (str): The organization's website.
        logo_url (str): The URL to the organization's logo.
        owner (UserDetailSerializer): The owner of the organization.
        member_count (int): The number of members in the organization.
        is_active (bool): Whether the organization is active.
        created_at (datetime): The date and time the organization was created.
        updated_at (datetime): The date and time the organization was last updated.

    Meta:
        model (Organization): The model class.
        fields (list): The fields to include in the serializer.
        read_only_fields (list): Fields that are read-only.
    """

    # Logo URL field
    logo_url = serializers.URLField(
        read_only=True,
        help_text=_("URL to the organization's logo."),
    )

    # Member count field
    member_count = serializers.IntegerField(
        read_only=True,
        help_text=_("Number of members in the organization."),
    )

    # Owner serializer
    owner = UserDetailSerializer(read_only=True)

    # Meta class for OrganizationSerializer configuration
    class Meta:
        """Meta class for OrganizationSerializer configuration.

        Attributes:
            model (Organization): The model class.
            fields (list): The fields to include in the serializer.
            read_only_fields (list): Fields that are read-only.
        """

        # Model to use for the serializer
        model = Organization

        # Fields to include in the serializer
        fields = [
            "id",
            "name",
            "description",
            "website",
            "logo_url",
            "owner",
            "member_count",
            "is_active",
            "created_at",
            "updated_at",
        ]

        # Read-only fields
        read_only_fields = [
            "id",
            "owner",
            "is_active",
            "created_at",
            "updated_at",
        ]


# Organization creation serializer
class OrganizationCreateSerializer(serializers.ModelSerializer):
    """Organization creation serializer.

    This serializer handles the creation of new organizations. It validates that
    the user has not exceeded the maximum number of organizations they can create.
    It also ensures a user cannot create multiple organizations with the same name.

    Meta:
        model (Organization): The Organization model.
        fields (list): The fields to include in the serializer.
        extra_kwargs (dict): Additional field configurations.

    Raises:
        serializers.ValidationError: If user has already created maximum organizations.
        serializers.ValidationError: If user already has an organization with the same name.

    Returns:
        Organization: The newly created organization instance.
    """

    # Meta class for OrganizationCreateSerializer configuration
    class Meta:
        """Meta class for OrganizationCreateSerializer configuration.

        Attributes:
            model (Organization): The model class.
            fields (list): The fields to include in the serializer.
            extra_kwargs (dict): Additional field configurations.
        """

        # Model to use for the serializer
        model = Organization

        # Fields to include in the serializer
        fields = [
            "name",
            "description",
            "website",
        ]

        # Extra kwargs
        extra_kwargs = {
            "name": {"required": True},
            "description": {"required": False},
            "website": {"required": False},
        }

    # Validate the serializer data
    def validate(self, attrs):
        """Validate the serializer data.

        This method validates that:
        1. The user has not exceeded the maximum number of organizations they can create (3).
        2. The user does not already have an organization with the same name.

        Args:
            attrs (dict): The attributes to validate.

        Returns:
            dict: The validated attributes.

        Raises:
            serializers.ValidationError: If the user has already reached the limit.
            serializers.ValidationError: If the user already has an organization with the same name.
        """

        # Get the user from the context
        user = self.context["request"].user

        # Check if the user has already created the maximum number of organizations
        if user.owned_organizations.count() >= Organization.MAX_ORGANIZATIONS_PER_USER:
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        f"You can only create a maximum of {Organization.MAX_ORGANIZATIONS_PER_USER} organizations.",
                    ],
                },
            )

        # Get the organization name
        organization_name = attrs.get("name")

        # Check if the user already has an organization with the same name
        if (
            organization_name
            and user.owned_organizations.filter(name=organization_name).exists()
        ):
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "name": [
                        "You already have an organization with this name.",
                    ],
                },
            )

        # Return the validated attributes
        return attrs

    # Create a new organization
    def create(self, validated_data):
        """Create a new organization.

        This method creates a new organization with the owner set to the current user.

        Args:
            validated_data (dict): The validated data.

        Returns:
            Organization: The newly created organization.
        """

        # Get the user from the context
        user = self.context["request"].user

        # Create the organization
        organization = Organization.objects.create(owner=user, **validated_data)

        # Add the owner as a member of the organization
        organization.add_member(user)

        # Return the organization
        return organization


# Organization creation success response serializer
class OrganizationCreateSuccessResponseSerializer(GenericResponseSerializer):
    """Organization creation success response serializer.

    This serializer defines the structure of the successful organization creation response.
    It includes a status code and an organization object.

    Attributes:
        status_code (int): The status code of the response.
        organization (OrganizationSerializer): The organization detail serializer.
    """

    # Status code
    status_code = serializers.IntegerField(default=status.HTTP_201_CREATED)

    # Organization serializer
    organization = OrganizationSerializer(
        read_only=True,
        help_text=_("The created organization."),
    )


# Organization creation error response serializer
class OrganizationCreateErrorResponseSerializer(GenericResponseSerializer):
    """Organization creation error response serializer (for schema).

    This serializer defines the structure of the wrapped validation error response.

    Attributes:
        status_code (int): The status code of the response.
        errors (OrganizationCreateErrorsDetailSerializer): The errors detail serializer.
    """

    # Nested serializer defining the structure of the actual errors
    class OrganizationCreateErrorsDetailSerializer(serializers.Serializer):
        """Organization Creation Errors detail serializer.

        Attributes:
            name (list): Errors related to the name field.
            description (list): Errors related to the description field.
            website (list): Errors related to the website field.
            non_field_errors (list): Non-field specific errors.
        """

        name = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the name field."),
        )
        description = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the description field."),
        )
        website = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the website field."),
        )
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Non-field specific errors (including limit warnings)."),
        )

    # Override status_code from GenericResponseSerializer
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        help_text=_("HTTP status code indicating a bad request."),
    )

    # Define the 'errors' field containing the validation error details
    errors = OrganizationCreateErrorsDetailSerializer(
        help_text=_("Object containing validation errors."),
    )


# Organization logo upload serializer
class OrganizationLogoSerializer(serializers.Serializer):
    """Organization logo upload serializer.

    This serializer handles the upload of organization logos.
    It validates that the file is a valid image (jpg/jpeg/png).

    Attributes:
        logo (ImageField): The logo file to upload.
    """

    # Logo field
    logo = serializers.ImageField(
        required=True,
        help_text=_("The logo file to upload. Must be a valid jpg/jpeg/png file."),
        label=_("Logo"),
    )

    # Validate the logo
    def validate_logo(self, value):
        """Validate the logo file.

        Ensures the file is a valid image with an allowed extension.

        Args:
            value (InMemoryUploadedFile): The uploaded file.

        Returns:
            InMemoryUploadedFile: The validated file.

        Raises:
            serializers.ValidationError: If the file is not a valid image or has a disallowed extension.
        """

        # Check if the file is an image
        if not value.content_type.startswith("image"):
            # Raise a validation error
            raise serializers.ValidationError(
                _("Uploaded file is not an image."),
            )

        # Get the file extension
        file_extension = value.name.split(".")[-1].lower()

        # Define allowed extensions
        allowed_extensions = ["jpg", "jpeg", "png"]

        # Check if the extension is allowed
        if file_extension not in allowed_extensions:
            # Raise a validation error
            raise serializers.ValidationError(
                _("Only jpg, jpeg, and png files are allowed."),
            )

        # Return the validated file
        return value


# Organization logo upload success response serializer
class OrganizationLogoSuccessResponseSerializer(GenericResponseSerializer):
    """Organization logo upload success response serializer.

    This serializer defines the structure of the successful logo upload response.
    It includes a status code and the updated organization object.

    Attributes:
        status_code (int): The status code of the response.
        organization (OrganizationSerializer): The organization detail serializer.
    """

    # Status code
    status_code = serializers.IntegerField(default=200)

    # Organization serializer
    organization = OrganizationSerializer(
        read_only=True,
        help_text=_("The updated organization with new logo."),
    )


# Organization logo upload error response serializer
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
    )

    # Errors
    errors = OrganizationLogoErrorsDetailSerializer(
        help_text=_("Object containing validation errors."),
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
        default="Organization not found or you are not the owner.",
        read_only=True,
    )


# Organization Detail Response Serializer
class OrganizationDetailResponseSerializer(GenericResponseSerializer):
    """Organization detail response serializer.

    This serializer defines the structure of the organization detail response.
    It includes a status code and an organization object.

    Attributes:
        status_code (int): The status code of the response.
        organization (OrganizationSerializer): The organization detail serializer.
    """

    # Status code
    status_code = serializers.IntegerField(default=status.HTTP_200_OK)

    # Organization serializer
    organization = OrganizationSerializer(
        help_text=_("The organization details."),
    )


# Organization Not Found Response Serializer
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
    )

    # Error message
    error = serializers.CharField(
        default="Organization not found or you don't have permission to view this organization.",
        read_only=True,
    )


# Organization List Response Serializer
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
        help_text=_("List of organizations owned by the user."),
    )


# Organization Membership List Response Serializer
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
        help_text=_("List of organizations where the user is a member or owner."),
    )


# Authentication Error Response Serializer
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
        default="Authentication credentials were not provided.",
        read_only=True,
    )
