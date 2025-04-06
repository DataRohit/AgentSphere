# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Project imports
from apps.common.serializer import GenericResponseSerializer
from apps.organization.models import Organization, OrganizationOwnershipTransfer
from apps.users.models import User
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
            ) from None

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
            ) from None

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
            ) from None

        # Get the file extension
        file_extension = value.name.split(".")[-1].lower()

        # Define allowed extensions
        allowed_extensions = ["jpg", "jpeg", "png"]

        # Check if the extension is allowed
        if file_extension not in allowed_extensions:
            # Raise a validation error
            raise serializers.ValidationError(
                _("Only jpg, jpeg, and png files are allowed."),
            ) from None

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


# Organization Member Add Serializer
class OrganizationMemberAddSerializer(serializers.Serializer):
    """Organization member add serializer.

    Handles adding a new member to an organization using user's ID, email, or username.
    Exactly one identifier (user_id, email, or username) must be provided.

    Attributes:
        user_id (UUID, optional): The ID of the user to add.
        email (str, optional): The email of the user to add.
        username (str, optional): The username of the user to add.
    """

    # User identifiers (optional, but one is required)
    user_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text=_("The ID of the user to add as a member."),
    )
    email = serializers.EmailField(
        required=False,
        allow_null=True,
        help_text=_("The email of the user to add as a member."),
    )
    username = serializers.CharField(
        required=False,
        allow_null=True,
        help_text=_("The username of the user to add as a member."),
    )

    # Store the resolved user
    _user_to_add = None

    # Validate the input data
    def validate(self, attrs: dict) -> dict:
        """Validate the input data.

        Ensures exactly one identifier is provided and the user is valid for addition.

        Args:
            attrs (dict): The input data.

        Returns:
            dict: The validated data.

        Raises:
            serializers.ValidationError: If the input data is invalid.
            User.DoesNotExist: If the user does not exist.
            Organization.DoesNotExist: If the organization does not exist.
            ValueError: If the organization is not provided in the context.
        """

        # Get the user identifiers
        user_id = attrs.get("user_id")
        email = attrs.get("email")
        username = attrs.get("username")

        # Check if exactly one identifier is provided
        provided_identifiers = [i for i in [user_id, email, username] if i is not None]
        if len(provided_identifiers) != 1:
            # Raise a validation error if the input data is invalid
            raise serializers.ValidationError(
                _("Exactly one of user_id, email, or username must be provided."),
            )

        # Check if the identifier is valid
        if not provided_identifiers:
            # Raise a validation error if the input data is invalid
            raise serializers.ValidationError(
                _("No valid identifier provided."),
            )

        # Get the organization from context
        organization = self.context.get("organization")

        # Check if the organization is provided in the context
        if not organization:
            # This should ideally not happen if context is always passed correctly
            raise serializers.ValidationError(
                _("Organization context is missing."),
            )

        # Initialize the user variable
        user = None

        # Try to find the user based on the provided identifier
        try:
            # Find the user based on the provided identifier
            if user_id:
                # Find the user by ID
                user = User.objects.get(id=user_id)
                field_name = "user_id"

            elif email:
                # Find the user by email
                user = User.objects.get(email=email)
                field_name = "email"

            elif username:
                # Find the user by username
                user = User.objects.get(username=username)
                field_name = "username"

        except User.DoesNotExist:
            # Raise a validation error if the user does not exist
            raise serializers.ValidationError(
                {
                    field_name: _("User with this %s does not exist.")
                    % field_name.replace("_", " "),
                },
            ) from None

        # Check if the user is the owner
        if user == organization.owner:
            # Raise a validation error if the user is the owner
            raise serializers.ValidationError(
                {
                    field_name: _(
                        "User is the owner of this organization and is already a member.",
                    ),
                },
            )

        # Check if the user is already a member
        if user in organization.members.all():
            # Raise a validation error if the user is already a member
            raise serializers.ValidationError(
                {
                    field_name: _(
                        "User is already a member of this organization.",
                    ),
                },
            )

        # Store the user for the view to use
        self._user_to_add = user

        # Return the validated attributes
        return attrs

    # Getter for the resolved user
    def get_user(self) -> User:
        """Get the resolved user object."""

        # Return the resolved user
        return self._user_to_add


# Organization Member Add Success Response Serializer
class OrganizationMemberAddSuccessResponseSerializer(GenericResponseSerializer):
    """Organization member add success response serializer.

    This serializer defines the structure of the successful member add response.
    It includes a status code and the updated organization object.

    Attributes:
        status_code (int): The status code of the response.
        organization (OrganizationSerializer): The organization detail serializer.
    """

    # Status code
    status_code = serializers.IntegerField(default=status.HTTP_200_OK)

    # Organization serializer
    organization = OrganizationSerializer(
        help_text=_("The updated organization with the new member."),
    )


# Organization Member Add Error Response Serializer
class OrganizationMemberAddErrorResponseSerializer(GenericResponseSerializer):
    """Organization member add error response serializer.

    This serializer defines the structure of the error response for member add.

    Attributes:
        status_code (int): The status code of the response.
        errors (OrganizationMemberAddErrorsDetailSerializer): The errors detail serializer.
    """

    # Nested serializer defining the structure of the actual errors
    class OrganizationMemberAddErrorsDetailSerializer(serializers.Serializer):
        """Organization Member Add Errors detail serializer.

        Attributes:
            user_id (list): Errors related to the user_id field.
            email (list): Errors related to the email field.
            username (list): Errors related to the username field.
            non_field_errors (list): Non-field specific errors (e.g., multiple identifiers provided).
        """

        # User ID field errors
        user_id = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the user_id field."),
        )

        # Email field errors
        email = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the email field."),
        )

        # Username field errors
        username = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the username field."),
        )

        # Non-field errors
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_(
                "Non-field specific errors (e.g., provide exactly one identifier).",
            ),
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        help_text=_("HTTP status code indicating a bad request."),
    )

    # Errors
    errors = OrganizationMemberAddErrorsDetailSerializer(
        help_text=_("Object containing validation errors."),
    )


# Organization Member Remove Serializer
class OrganizationMemberRemoveSerializer(serializers.Serializer):
    """Organization member remove serializer.

    Handles removing a member from an organization using user's ID, email, or username.
    Exactly one identifier (user_id, email, or username) must be provided.

    Attributes:
        user_id (UUID, optional): The ID of the user to remove.
        email (str, optional): The email of the user to remove.
        username (str, optional): The username of the user to remove.
    """

    # User identifiers (optional, but one is required)
    user_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text=_("The ID of the user to remove from the organization."),
    )
    email = serializers.EmailField(
        required=False,
        allow_null=True,
        help_text=_("The email of the user to remove from the organization."),
    )
    username = serializers.CharField(
        required=False,
        allow_null=True,
        help_text=_("The username of the user to remove from the organization."),
    )

    # Store the resolved user
    _user_to_remove = None

    # Validate the input data
    def validate(self, attrs: dict) -> dict:
        """Validate the input data.

        Ensures exactly one identifier is provided and the user is valid for removal.

        Args:
            attrs (dict): The input data.

        Returns:
            dict: The validated data.

        Raises:
            serializers.ValidationError: If the input data is invalid.
            User.DoesNotExist: If the user does not exist.
            Organization.DoesNotExist: If the organization does not exist.
            ValueError: If the organization is not provided in the context.
        """

        # Get the user identifiers
        user_id = attrs.get("user_id")
        email = attrs.get("email")
        username = attrs.get("username")

        # Check if exactly one identifier is provided
        provided_identifiers = [i for i in [user_id, email, username] if i is not None]
        if len(provided_identifiers) != 1:
            # Raise a validation error if the input data is invalid
            raise serializers.ValidationError(
                _("Exactly one of user_id, email, or username must be provided."),
            )

        # Get the organization from context
        organization = self.context.get("organization")
        if not organization:
            # This should ideally not happen if context is always passed correctly
            raise serializers.ValidationError(
                _("Organization context is missing."),
            )

        # Find the user based on the provided identifier
        user = None
        try:
            # Find the user based on the provided identifier
            if user_id:
                # Find the user by ID
                user = User.objects.get(id=user_id)
                field_name = "user_id"

            elif email:
                # Find the user by email
                user = User.objects.get(email=email)
                field_name = "email"

            elif username:
                # Find the user by username
                user = User.objects.get(username=username)
                field_name = "username"

        except User.DoesNotExist:
            # Raise a validation error if the user does not exist
            raise serializers.ValidationError(
                {
                    field_name: _("User with this %s does not exist.")
                    % field_name.replace("_", " "),
                },
            ) from None

        # Check if the user is the owner
        if user == organization.owner:
            # Raise a validation error if the user is the owner
            raise serializers.ValidationError(
                {
                    field_name: _(
                        "Cannot remove the owner from the organization.",
                    ),
                },
            )

        # Check if the user is actually a member
        if user not in organization.members.all():
            # Raise a validation error if the user is not a member
            raise serializers.ValidationError(
                {
                    field_name: _(
                        "User is not a member of this organization.",
                    ),
                },
            )

        # Store the user for the view to use
        self._user_to_remove = user

        # Return the validated attributes
        return attrs

    # Getter for the resolved user
    def get_user(self) -> User:
        """Get the resolved user object."""

        # Return the resolved user
        return self._user_to_remove


# Organization Member Remove Success Response Serializer
class OrganizationMemberRemoveSuccessResponseSerializer(GenericResponseSerializer):
    """Organization member remove success response serializer.

    This serializer defines the structure of the successful member remove response.
    It includes a status code and the updated organization object.

    Attributes:
        status_code (int): The status code of the response.
        organization (OrganizationSerializer): The organization detail serializer.
    """

    # Status code
    status_code = serializers.IntegerField(default=status.HTTP_200_OK)

    # Organization serializer
    organization = OrganizationSerializer(
        help_text=_("The updated organization after removing the member."),
    )


# Organization Member Remove Error Response Serializer
class OrganizationMemberRemoveErrorResponseSerializer(GenericResponseSerializer):
    """Organization member remove error response serializer.

    This serializer defines the structure of the error response for member remove.

    Attributes:
        status_code (int): The status code of the response.
        errors (OrganizationMemberRemoveErrorsDetailSerializer): The errors detail serializer.
    """

    # Nested serializer defining the structure of the actual errors
    class OrganizationMemberRemoveErrorsDetailSerializer(serializers.Serializer):
        """Organization Member Remove Errors detail serializer.

        Attributes:
            user_id (list): Errors related to the user_id field.
            email (list): Errors related to the email field.
            username (list): Errors related to the username field.
            non_field_errors (list): Non-field specific errors (e.g., multiple identifiers provided).
        """

        # User ID field errors
        user_id = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the user_id field."),
        )

        # Email field errors
        email = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the email field."),
        )

        # Username field errors
        username = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the username field."),
        )

        # Non-field errors
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_(
                "Non-field specific errors (e.g., provide exactly one identifier).",
            ),
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        help_text=_("HTTP status code indicating a bad request."),
    )

    # Errors
    errors = OrganizationMemberRemoveErrorsDetailSerializer(
        help_text=_("Object containing validation errors."),
    )


# Organization Ownership Transfer Initialization serializer
class OrganizationOwnershipTransferInitSerializer(serializers.Serializer):
    """Organization Ownership Transfer Initialization serializer.

    Handles initializing an ownership transfer using user's ID, email, or username.
    Exactly one identifier (user_id, email, or username) must be provided.

    Attributes:
        user_id (UUID, optional): The ID of the user to transfer ownership to.
        email (str, optional): The email of the user to transfer ownership to.
        username (str, optional): The username of the user to transfer ownership to.
    """

    # User identifiers (optional, but one is required)
    user_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text=_("The ID of the user to transfer ownership to."),
    )
    email = serializers.EmailField(
        required=False,
        allow_null=True,
        help_text=_("The email of the user to transfer ownership to."),
    )
    username = serializers.CharField(
        required=False,
        allow_null=True,
        help_text=_("The username of the user to transfer ownership to."),
    )

    # Store the resolved user
    _new_owner = None

    # Validate the serializer data
    def validate(self, attrs: dict) -> dict:
        """Validate the serializer data."""
        # Validate identifiers
        self._validate_identifiers(attrs)

        # Get and validate organization and users
        organization = self._validate_organization()
        current_user = self._validate_current_user()

        # Validate ownership
        self._validate_ownership(organization, current_user)

        # Resolve the new owner
        self._resolve_new_owner(attrs)

        # Validate new owner is not current owner
        self._validate_not_self_transfer()

        # Validate new owner is a member
        self._validate_new_owner_membership(organization)

        # Return the validated attributes
        return attrs

    # Validate identifiers
    def _validate_identifiers(self, attrs: dict) -> None:
        """Validate that exactly one identifier is provided."""

        # Get the provided identifiers
        identifiers = ["user_id", "email", "username"]

        # Get the provided identifiers
        provided_identifiers = [
            identifier for identifier in identifiers if attrs.get(identifier)
        ]

        # If no identifiers are provided
        if len(provided_identifiers) == 0:
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "You must provide exactly one of: user_id, email, or username.",
                    ],
                },
            ) from None

        # If more than one identifier is provided
        if len(provided_identifiers) > 1:
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "You must provide exactly one of: user_id, email, or username.",
                    ],
                },
            ) from None

    # Validate organization
    def _validate_organization(self) -> Organization:
        """Validate organization exists."""

        # Get the organization from the context
        organization = self.context.get("organization")

        # If the organization is not found
        if not organization:
            # Raise a validation error
            raise serializers.ValidationError(
                {"non_field_errors": ["Organization not found."]},
            ) from None

        # Return the organization
        return organization

    # Validate current user
    def _validate_current_user(self) -> User:
        """Validate current user is authenticated."""

        # Get the current user from the context
        current_user = self.context.get("request").user

        # If the current user is not found
        if not current_user:
            raise serializers.ValidationError(
                {"non_field_errors": ["User not authenticated."]},
            ) from None

        # Return the current user
        return current_user

    # Validate ownership
    def _validate_ownership(
        self,
        organization: Organization,
        current_user: User,
    ) -> None:
        """Validate current user is the owner."""

        # If the current user is not the owner
        if organization.owner != current_user:
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "Only the owner of the organization can transfer ownership.",
                    ],
                },
            ) from None

    # Resolve the new owner
    def _resolve_new_owner(self, attrs: dict) -> None:
        """Resolve the new owner based on the provided identifier."""

        # Try to get the new owner
        try:
            # If user_id is provided, get the user by ID
            if attrs.get("user_id"):
                self._new_owner = User.objects.get(id=attrs["user_id"])

            # If email is provided, get the user by email
            elif attrs.get("email"):
                self._new_owner = User.objects.get(email=attrs["email"])

            # If username is provided, get the user by username
            elif attrs.get("username"):
                self._new_owner = User.objects.get(username=attrs["username"])

        # If the user does not exist
        except User.DoesNotExist:
            # Get the field name that was provided
            field_name = next(
                k for k in ["user_id", "email", "username"] if attrs.get(k)
            )

            # Raise a validation error
            raise serializers.ValidationError(
                {
                    field_name: [
                        f"User with this {field_name.replace('_', ' ')} does not exist.",
                    ],
                },
            ) from None

    # Validate not self transfer
    def _validate_not_self_transfer(self) -> None:
        """Validate new owner is not the current owner."""

        # Get the current user from the context
        current_user = self.context.get("request").user

        # If the new owner is the current user
        if self._new_owner == current_user:
            raise serializers.ValidationError(
                {"non_field_errors": ["You cannot transfer ownership to yourself."]},
            ) from None

    # Validate new owner membership
    def _validate_new_owner_membership(self, organization: Organization) -> None:
        """Validate new owner is a member of the organization."""

        # If the new owner is not a member of the organization
        if self._new_owner not in organization.members.all():
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "The new owner must be a member of the organization.",
                    ],
                },
            ) from None

    # Get the resolved user
    def get_user(self) -> User:
        """Get the resolved user.

        Returns:
            User: The resolved user.
        """

        # Return the resolved user
        return self._new_owner


# Organization Ownership Transfer Init Response serializer
class OrganizationOwnershipTransferInitResponseSerializer(serializers.ModelSerializer):
    """Organization Ownership Transfer Init Response serializer.

    This serializer provides a simplified representation of the OrganizationOwnershipTransfer model
    specifically for the initialization response.

    Attributes:
        id (UUID): The transfer's ID.
        organization (OrganizationSerializer): The organization being transferred.
        new_owner (UserDetailSerializer): The proposed new owner of the organization.
        expiration_time (datetime): When the transfer request expires.

    Meta:
        model (OrganizationOwnershipTransfer): The model class.
        fields (list): The fields to include in the serializer.
        read_only_fields (list): Fields that are read-only.
    """

    # Organization serializer
    organization = OrganizationSerializer(read_only=True)

    # New owner serializer
    new_owner = UserDetailSerializer(read_only=True)

    # Meta class for OrganizationOwnershipTransferInitResponseSerializer configuration
    class Meta:
        """Meta class for OrganizationOwnershipTransferInitResponseSerializer configuration.

        Attributes:
            model (OrganizationOwnershipTransfer): The model class.
            fields (list): The fields to include in the serializer.
            read_only_fields (list): Fields that are read-only.
        """

        # Model to use for the serializer
        model = OrganizationOwnershipTransfer

        # Fields to include in the serializer
        fields = [
            "id",
            "organization",
            "new_owner",
            "expiration_time",
        ]

        # Read-only fields
        read_only_fields = fields


# Organization Ownership Transfer Initialization Error Response serializer
class OrganizationOwnershipTransferInitErrorResponseSerializer(
    GenericResponseSerializer,
):
    """Organization Ownership Transfer Initialization error response serializer.

    This serializer defines the structure of the error response for transfer initialization.

    Attributes:
        status_code (int): The status code of the response.
        errors (OrganizationOwnershipTransferInitErrorsDetailSerializer): The errors detail serializer.
    """

    # Nested serializer defining the structure of the actual errors
    class OrganizationOwnershipTransferInitErrorsDetailSerializer(
        serializers.Serializer,
    ):
        """Organization Ownership Transfer Initialization Errors detail serializer.

        Attributes:
            user_id (list): Errors related to the user_id field.
            email (list): Errors related to the email field.
            username (list): Errors related to the username field.
            non_field_errors (list): Non-field specific errors.
        """

        # User ID field errors
        user_id = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the user_id field."),
        )

        # Email field errors
        email = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the email field."),
        )

        # Username field errors
        username = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the username field."),
        )

        # Non-field errors
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_(
                "Non-field specific errors (e.g., provide exactly one identifier).",
            ),
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        help_text=_("HTTP status code indicating a bad request."),
    )

    # Errors
    errors = OrganizationOwnershipTransferInitErrorsDetailSerializer(
        help_text=_("Validation errors."),
    )


# Organization Ownership Transfer Status Success Response serializer
class OrganizationOwnershipTransferStatusSuccessResponseSerializer(
    GenericResponseSerializer,
):
    """Organization Ownership Transfer Status success response serializer.

    This serializer defines the structure of the successful transfer status response.
    It includes a status code and a message field.

    Attributes:
        status_code (int): The status code of the response.
        organization (OrganizationOwnershipTransferStatusSuccessMessageSerializer): The organization detail serializer.
    """

    # Nested serializer defining the structure of the actual message
    class OrganizationOwnershipTransferStatusSuccessMessageSerializer(
        serializers.Serializer,
    ):
        """Organization Ownership Transfer Status success response message serializer.

        Attributes:
            message (str): A success message.
        """

        message = serializers.CharField(
            help_text=_("Success message."),
        )

    # Status code
    status_code = serializers.IntegerField(default=status.HTTP_200_OK)

    # Organization
    organization = OrganizationOwnershipTransferStatusSuccessMessageSerializer(
        help_text=_("The organization details."),
    )


# Organization Ownership Transfer Status Error Response serializer
class OrganizationOwnershipTransferStatusErrorResponseSerializer(
    GenericResponseSerializer,
):
    """Organization Ownership Transfer Status error response serializer.

    This serializer defines the structure of the error response for transfer status actions.

    Attributes:
        status_code (int): The status code of the response.
        error (str): An error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        help_text=_("HTTP status code indicating a bad request."),
    )

    # Error
    error = serializers.CharField(
        help_text=_("Error message."),
    )


# Organization Ownership Transfer Not Found Response serializer
class OrganizationOwnershipTransferNotFoundResponseSerializer(
    GenericResponseSerializer,
):
    """Organization Ownership Transfer not found response serializer.

    This serializer defines the structure of the not found response for transfer requests
    when the transfer doesn't exist or the user doesn't have permission.

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
        default="Organization ownership transfer not found or you don't have permission.",
        read_only=True,
        help_text=_("Error message indicating the transfer was not found."),
    )


# Organization Update Serializer
class OrganizationUpdateSerializer(serializers.ModelSerializer):
    """Organization update serializer.

    This serializer handles updating existing organizations. It validates that
    the name is unique among the user's organizations if it is being changed.

    Attributes:
        name (str): The organization's name.
        description (str): The organization's description.
        website (str): The organization's website.

    Meta:
        model (Organization): The Organization model.
        fields (list): The fields that can be updated.
        extra_kwargs (dict): Additional field configurations.
    """

    # Meta class for OrganizationUpdateSerializer configuration
    class Meta:
        """Meta class for OrganizationUpdateSerializer configuration."""

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
            "name": {"required": False},
            "description": {"required": False},
            "website": {"required": False},
        }

    # Validate the serializer data
    def validate_name(self, value):
        """Validate that the name is unique among the user's organizations.

        Args:
            value (str): The name to validate.

        Returns:
            str: The validated name.

        Raises:
            serializers.ValidationError: If the user already has an organization with this name.
        """

        # Get the current organization
        organization = self.instance

        # Get the user from the context
        user = self.context["request"].user

        # Check if the name is changing
        if value != organization.name:
            # Check if the user already has an organization with this name
            if user.owned_organizations.filter(name=value).exists():
                # Raise a validation error
                raise serializers.ValidationError(
                    _("You already have an organization with this name."),
                ) from None

        # Return the validated name
        return value


# Organization Update Success Response Serializer
class OrganizationUpdateSuccessResponseSerializer(GenericResponseSerializer):
    """Organization update success response serializer.

    This serializer defines the structure of the successful organization update response.
    It includes a status code and the updated organization object.

    Attributes:
        status_code (int): The status code of the response.
        organization (OrganizationSerializer): The updated organization.
    """

    # Status code
    status_code = serializers.IntegerField(default=status.HTTP_200_OK)

    # Organization serializer
    organization = OrganizationSerializer(
        read_only=True,
        help_text=_("The updated organization."),
    )


# Organization Update Error Response Serializer
class OrganizationUpdateErrorResponseSerializer(GenericResponseSerializer):
    """Organization update error response serializer.

    This serializer defines the structure of the error response for organization update.

    Attributes:
        status_code (int): The status code of the response.
        errors (OrganizationUpdateErrorsDetailSerializer): The errors detail serializer.
    """

    # Nested serializer defining the structure of the actual errors
    class OrganizationUpdateErrorsDetailSerializer(serializers.Serializer):
        """Organization Update Errors detail serializer.

        Attributes:
            name (list): Errors related to the name field.
            description (list): Errors related to the description field.
            website (list): Errors related to the website field.
            non_field_errors (list): Non-field specific errors.
        """

        # Name field errors
        name = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the name field."),
        )

        # Description field errors
        description = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the description field."),
        )

        # Website field errors
        website = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the website field."),
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
    errors = OrganizationUpdateErrorsDetailSerializer(
        help_text=_("Object containing validation errors."),
    )
