# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.common.serializers import GenericResponseSerializer
from apps.organization.models import Organization
from apps.organization.serializers.organization import OrganizationSerializer


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
    def validate(self, attrs: dict) -> dict:
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
        if organization_name and user.owned_organizations.filter(name=organization_name).exists():
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
    status_code = serializers.IntegerField(
        default=status.HTTP_201_CREATED,
        read_only=True,
        help_text=_("HTTP status code indicating a successful creation."),
    )

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

        # Name field
        name = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the name field."),
        )

        # Description field
        description = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the description field."),
        )

        # Website field
        website = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the website field."),
        )

        # Non-field errors
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Non-field specific errors (including limit warnings)."),
        )

    # Override status_code from GenericResponseSerializer
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        help_text=_("HTTP status code indicating a bad request."),
        read_only=True,
    )

    # Define the 'errors' field containing the validation error details
    errors = OrganizationCreateErrorsDetailSerializer(
        help_text=_("Object containing validation errors."),
        read_only=True,
    )
