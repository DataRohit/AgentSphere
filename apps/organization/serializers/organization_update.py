# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Project imports
from apps.common.serializers import GenericResponseSerializer
from apps.organization.models import Organization
from apps.organization.serializers.organization import OrganizationSerializer


# Organization update serializer
class OrganizationUpdateSerializer(serializers.ModelSerializer):
    """Organization update serializer.

    This serializer handles updating existing organizations. It validates that
    the organization name is not already taken by another organization owned by the same user.

    Meta:
        model (Organization): The Organization model.
        fields (list): The fields that can be updated.
        extra_kwargs (dict): Additional field configurations.

    Raises:
        serializers.ValidationError: If user already has another organization with the same name.

    Returns:
        Organization: The updated organization instance.
    """

    # Meta class for OrganizationUpdateSerializer configuration
    class Meta:
        """Meta class for OrganizationUpdateSerializer configuration.

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
            "name": {"required": False},
            "description": {"required": False},
            "website": {"required": False},
        }

    # Validate the serializer data
    def validate_name(self, value):
        """Validate the name field.

        This method validates that the user does not already have another
        organization with the same name.

        Args:
            value (str): The name to validate.

        Returns:
            str: The validated name.

        Raises:
            serializers.ValidationError: If the user already has another org with this name.
        """

        # Get the organization from the context
        organization = self.context.get("organization")
        user = self.context.get("user")

        # If the name is not changing, or if it's empty, skip validation
        if not value or (organization and organization.name == value):
            return value

        # Check if the user already has an organization with the same name
        if (
            user
            and organization
            and user.owned_organizations.exclude(id=organization.id)
            .filter(name=value)
            .exists()
        ):
            # Raise a validation error
            raise serializers.ValidationError(
                ["You already have another organization with this name."],
            ) from None

        # Return the validated name
        return value

    # Update the organization
    def update(self, instance, validated_data):
        """Update the organization.

        This method updates the organization with the validated data.

        Args:
            instance (Organization): The organization to update.
            validated_data (dict): The validated data.

        Returns:
            Organization: The updated organization.
        """

        # Update the organization
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.website = validated_data.get("website", instance.website)
        instance.save()

        # Return the updated organization
        return instance


# Organization update success response serializer
class OrganizationUpdateSuccessResponseSerializer(GenericResponseSerializer):
    """Organization update success response serializer.

    This serializer defines the structure of the successful organization update response.
    It includes a status code and the updated organization object.

    Attributes:
        status_code (int): The status code of the response.
        organization (OrganizationSerializer): The organization detail serializer.
    """

    # Status code
    status_code = serializers.IntegerField(default=status.HTTP_200_OK)

    # Organization serializer
    organization = OrganizationSerializer(
        read_only=True,
        help_text=_("The updated organization."),
    )


# Organization update error response serializer
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
