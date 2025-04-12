# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Project imports
from apps.common.serializers import GenericResponseSerializer
from apps.organization.serializers.organization import OrganizationSerializer
from apps.users.models import User


# Organization Member Add Serializer
class OrganizationMemberAddSerializer(serializers.Serializer):
    """Organization member add serializer.

    Handles adding a new member to an organization using user's ID, email, or username.
    Exactly one identifier (user_id, email, or username) must be provided.
    An organization can have a maximum of 8 members (including the owner).

    Attributes:
        user_id (UUID, optional): The ID of the user to add.
        email (str, optional): The email of the user to add.
        username (str, optional): The username of the user to add.
    """

    # User ID field
    user_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text=_("The ID of the user to add as a member."),
    )

    # Email field
    email = serializers.EmailField(
        required=False,
        allow_null=True,
        help_text=_("The email of the user to add as a member."),
    )

    # Username field
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
        """Get the resolved user object.

        This method returns the resolved user object.

        Returns:
            User: The resolved user object.
        """

        # Return the resolved user
        return self._user_to_add


# Organization member add success response serializer
class OrganizationMemberAddSuccessResponseSerializer(GenericResponseSerializer):
    """Organization member add success response serializer.

    This serializer defines the structure of the successful member add response.
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
        help_text=_("The updated organization with the new member added."),
    )


# Organization member add error response serializer
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
                "Non-field specific errors.",
            ),
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code indicating a bad request."),
    )

    # Errors
    errors = OrganizationMemberAddErrorsDetailSerializer(
        help_text=_("Object containing validation errors."),
        read_only=True,
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

    # User ID field
    user_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text=_("The ID of the user to remove from the organization."),
    )

    # Email field
    email = serializers.EmailField(
        required=False,
        allow_null=True,
        help_text=_("The email of the user to remove from the organization."),
    )

    # Username field
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
        """Get the resolved user object.

        This method returns the resolved user object.

        Returns:
            User: The resolved user object.
        """

        # Return the resolved user
        return self._user_to_remove


# Organization member remove success response serializer
class OrganizationMemberRemoveSuccessResponseSerializer(GenericResponseSerializer):
    """Organization member remove success response serializer.

    This serializer defines the structure of the successful member remove response.
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
        help_text=_("The updated organization with the member removed."),
    )


# Organization member remove error response serializer
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
        read_only=True,
        help_text=_("HTTP status code indicating a bad request."),
    )

    # Errors
    errors = OrganizationMemberRemoveErrorsDetailSerializer(
        help_text=_("Object containing validation errors."),
        read_only=True,
    )
