# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Project imports
from apps.common.serializers import GenericResponseSerializer
from apps.organization.models import Organization
from apps.organization.serializers.organization import OrganizationSerializer
from apps.users.models import User


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
        """Validate the serializer data.

        This method validates the serializer data by ensuring that exactly one
        identifier (user_id, email, or username) is provided. It also validates
        that the organization exists, the current user is authenticated, and
        that the current user is the owner of the organization.

        Args:
            attrs (dict): The serializer data.

        Returns:
            dict: The validated attributes.
        """

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
        """Validate that exactly one identifier is provided.

        This method validates that exactly one identifier (user_id, email, or username)
        is provided in the serializer data. If no identifiers are provided, a validation
        error is raised. If more than one identifier is provided, a validation error is
        raised.

        Args:
            attrs (dict): The serializer data.
        """

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
        """Validate organization exists.

        This method validates that the organization exists in the context.
        If the organization is not found, a validation error is raised.

        Returns:
            Organization: The organization.
        """
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
        """Validate current user is authenticated.

        This method validates that the current user is authenticated.
        If the current user is not found, a validation error is raised.

        Returns:
            User: The current user.
        """
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
        """Validate current user is the owner.

        This method validates that the current user is the owner of the organization.
        If the current user is not the owner, a validation error is raised.

        Args:
            organization (Organization): The organization.
        """

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
        """Resolve the new owner based on the provided identifier.

        This method resolves the new owner based on the provided identifier
        (user_id, email, or username). If the user does not exist, a validation
        error is raised.

        Args:
            attrs (dict): The serializer data.
        """

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
        """Validate new owner is not the current owner.

        This method validates that the new owner is not the current user.
        If the new owner is the current user, a validation error is raised.
        """

        # Get the current user from the context
        current_user = self.context.get("request").user

        # If the new owner is the current user
        if self._new_owner == current_user:
            raise serializers.ValidationError(
                {"non_field_errors": ["You cannot transfer ownership to yourself."]},
            ) from None

    # Validate new owner membership
    def _validate_new_owner_membership(self, organization: Organization) -> None:
        """Validate new owner is a member of the organization.

        This method validates that the new owner is a member of the organization.
        If the new owner is not a member of the organization, a validation error is raised.

        Args:
            organization (Organization): The organization.
        """

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

        This method returns the resolved user.

        Returns:
            User: The resolved user.
        """

        # Return the resolved user
        return self._new_owner


# Organization ownership transfer initialization response serializer
class OrganizationOwnershipTransferInitResponseSerializer(GenericResponseSerializer):
    """Organization ownership transfer initialization response serializer.

    This serializer defines the structure of the successful transfer initialization response.
    It includes a status code, a message, and the transfer token.

    Attributes:
        status_code (int): The status code of the response.
        message (str): A message indicating the transfer was initiated successfully.
        token (str): The token that can be used to confirm the transfer.
        expires_at (datetime): The expiry time of the transfer token.
    """

    # Status code
    status_code = serializers.IntegerField(default=status.HTTP_200_OK)

    # Success message
    message = serializers.CharField(
        read_only=True,
        help_text=_("Message indicating the transfer was initiated successfully."),
    )

    # Transfer token
    token = serializers.CharField(
        read_only=True,
        help_text=_("The token that can be used to confirm the transfer."),
    )

    # Expiry time
    expires_at = serializers.DateTimeField(
        read_only=True,
        help_text=_("The expiry time of the transfer token."),
    )


# Organization ownership transfer initialization error response serializer
class OrganizationOwnershipTransferInitErrorResponseSerializer(
    GenericResponseSerializer,
):
    """Organization ownership transfer initialization error response serializer.

    This serializer defines the structure of the error response for transfer initialization.

    Attributes:
        status_code (int): The status code of the response.
        errors (TransferInitErrorsDetailSerializer): The errors detail serializer.
    """

    # Nested serializer defining the structure of the actual errors
    class TransferInitErrorsDetailSerializer(serializers.Serializer):
        """Transfer Initialization Errors detail serializer.

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
            help_text=_("Non-field specific errors."),
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        help_text=_("HTTP status code indicating a bad request."),
    )

    # Errors
    errors = TransferInitErrorsDetailSerializer(
        help_text=_("Object containing validation errors."),
    )


# Organization ownership transfer status success response serializer
class OrganizationOwnershipTransferStatusSuccessResponseSerializer(
    GenericResponseSerializer,
):
    """Organization ownership transfer status success response serializer.

    This serializer defines the structure of the successful transfer status response.
    It includes a status code, a message, and the updated organization object.

    Attributes:
        status_code (int): The status code of the response.
        message (str): A message indicating the transfer was completed successfully.
        organization (OrganizationSerializer): The updated organization with the new owner.
    """

    # Status code
    status_code = serializers.IntegerField(default=status.HTTP_200_OK)

    # Success message
    message = serializers.CharField(
        read_only=True,
        help_text=_("Message indicating the transfer was completed successfully."),
    )

    # Organization serializer
    organization = OrganizationSerializer(
        read_only=True,
        help_text=_("The updated organization with the new owner."),
    )


# Organization ownership transfer status error response serializer
class OrganizationOwnershipTransferStatusErrorResponseSerializer(
    GenericResponseSerializer,
):
    """Organization ownership transfer status error response serializer.

    This serializer defines the structure of the error response for transfer status.

    Attributes:
        status_code (int): The status code of the response.
        error (str): An error message explaining why the transfer failed.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        help_text=_("HTTP status code indicating a bad request."),
    )

    # Error message
    error = serializers.CharField(
        read_only=True,
        help_text=_("Error message explaining why the transfer failed."),
    )


# Organization ownership transfer not found response serializer
class OrganizationOwnershipTransferNotFoundResponseSerializer(
    GenericResponseSerializer,
):
    """Organization ownership transfer not found response serializer.

    This serializer defines the structure of the not found response for transfer actions
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
        default=_("Transfer not found or you do not have permission."),
        read_only=True,
        help_text=_("Error message explaining why the resource was not found."),
    )
