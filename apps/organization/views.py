# Third-party imports
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError

# Project imports
from apps.common.renderers import GenericJSONRenderer

# Import send_templated_mail at the top of the file
from apps.common.utils import send_templated_mail
from apps.organization.models import Organization, OrganizationOwnershipTransfer
from apps.organization.serializers import (
    OrganizationAuthErrorResponseSerializer,
    OrganizationCreateErrorResponseSerializer,
    OrganizationCreateSerializer,
    OrganizationCreateSuccessResponseSerializer,
    OrganizationDetailResponseSerializer,
    OrganizationListResponseSerializer,
    OrganizationLogoErrorResponseSerializer,
    OrganizationLogoNotFoundResponseSerializer,
    OrganizationLogoSerializer,
    OrganizationLogoSuccessResponseSerializer,
    OrganizationMemberAddErrorResponseSerializer,
    OrganizationMemberAddSerializer,
    OrganizationMemberAddSuccessResponseSerializer,
    OrganizationMemberRemoveErrorResponseSerializer,
    OrganizationMemberRemoveSerializer,
    OrganizationMemberRemoveSuccessResponseSerializer,
    OrganizationMembershipListResponseSerializer,
    OrganizationNotFoundResponseSerializer,
    OrganizationOwnershipTransferInitErrorResponseSerializer,
    OrganizationOwnershipTransferInitResponseSerializer,
    OrganizationOwnershipTransferInitSerializer,
    OrganizationOwnershipTransferInitSuccessResponseSerializer,
    OrganizationOwnershipTransferNotFoundResponseSerializer,
    OrganizationOwnershipTransferStatusErrorResponseSerializer,
    OrganizationOwnershipTransferStatusSuccessResponseSerializer,
    OrganizationSerializer,
    OrganizationUpdateErrorResponseSerializer,
    OrganizationUpdateSerializer,
    OrganizationUpdateSuccessResponseSerializer,
)

# Get the User model
User = get_user_model()


# Organization creation view
class OrganizationCreateView(APIView):
    """Organization creation view.

    This view allows authenticated users to create new organizations.
    A user is limited to creating a maximum of 3 organizations.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        object_label (str): The object label for the response.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Define the permission classes - require authentication
    permission_classes = [IsAuthenticated]

    # Define the object label
    object_label = "organization"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the organization creation view.

        This method handles exceptions for the organization creation view.

        Args:
            exc: The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return custom format for authentication errors
        if isinstance(exc, (AuthenticationFailed, TokenError)):
            return Response(
                {"error": str(exc)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Return the exception as a standard error
        return Response(
            {"error": str(exc)},
            status=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        )

    # Define the schema
    @extend_schema(
        tags=["Organizations"],
        summary="Create a new organization.",
        description=f"""
        Creates a new organization with the authenticated user as the owner.
        A user can create a maximum of {Organization.MAX_ORGANIZATIONS_PER_USER} organizations.
        The owner is automatically added as a member of the organization.
        """,
        request=OrganizationCreateSerializer,
        responses={
            status.HTTP_201_CREATED: OrganizationCreateSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: OrganizationCreateErrorResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        """Create a new organization.

        This method creates a new organization with the authenticated user as the owner.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Create a new organization instance
        serializer = OrganizationCreateSerializer(
            data=request.data,
            context={"request": request},
        )

        # Validate the serializer
        if serializer.is_valid():
            # Save the organization instance
            organization = serializer.save()

            # Serialize the created organization for the response body
            response_serializer = OrganizationSerializer(organization)

            # Return 201 Created with the serialized organization data
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED,
            )

        # Return 400 Bad Request with validation errors
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# Organization logo upload view
class OrganizationLogoUploadView(APIView):
    """Organization logo upload view.

    This view allows organization owners to upload a logo for their organization.
    If the organization already has a logo, the existing logo is deleted and replaced.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        parser_classes (list): The parser classes for handling file uploads.
        object_label (str): The object label for the response.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Define the permission classes - require authentication
    permission_classes = [IsAuthenticated]

    # Define the parser classes for handling file uploads
    parser_classes = [MultiPartParser, FormParser]

    # Define the object label
    object_label = "organization"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the organization logo upload view.

        This method handles exceptions for the organization logo upload view.

        Args:
            exc: The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return custom format for authentication errors
        if isinstance(exc, (AuthenticationFailed, TokenError)):
            return Response(
                {"error": str(exc)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Return the exception as a standard error
        return Response(
            {"error": str(exc)},
            status=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        )

    # Define the schema
    @extend_schema(
        tags=["Organizations"],
        summary="Upload or update an organization logo.",
        description="""
        Uploads or updates the logo for an organization. The authenticated user must be the owner.
        If the organization already has a logo, it will be deleted and replaced.
        The logo file must be a valid jpg, jpeg, or png image.
        """,
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {"logo": {"type": "string", "format": "binary"}},
            },
        },
        responses={
            status.HTTP_200_OK: OrganizationLogoSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: OrganizationLogoErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: OrganizationLogoNotFoundResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def put(self, request: Request, organization_id: str) -> Response:
        """Upload or update an organization logo.

        Args:
            request (Request): The HTTP request object.
            organization_id (str): The ID of the organization.

        Returns:
            Response: The HTTP response object.
        """

        try:
            # Get the organization by ID and check if the user is the owner
            organization = Organization.objects.get(
                id=organization_id,
                owner=request.user,
            )

        except Organization.DoesNotExist:
            # Return 404 Not Found if the organization doesn't exist or user is not the owner
            return Response(
                {
                    "error": "Organization not found or you are not the owner.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Create a serializer for the logo upload
        serializer = OrganizationLogoSerializer(data=request.data)

        # Validate the serializer
        if serializer.is_valid():
            # Get the uploaded logo file
            logo_file = serializer.validated_data["logo"]

            # Check if the organization already has a logo
            if organization.logo:
                # Delete the existing logo
                organization.logo.delete(save=False)

            # Get the file extension
            file_extension = logo_file.name.split(".")[-1].lower()

            # Create a new filename using the organization ID
            new_filename = f"{organization.id}.{file_extension}"

            # Update the logo file name before saving
            logo_file.name = new_filename

            # Update the organization with the new logo
            organization.logo = logo_file
            organization.save()

            # Serialize the updated organization for the response body
            response_serializer = OrganizationSerializer(organization)

            # Return 200 OK with the serialized organization data
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK,
            )

        # Return 400 Bad Request with validation errors
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# Organization Detail View
class OrganizationDetailView(APIView):
    """Organization detail view.

    This view allows organization owners and members to view organization details.
    Users who are not owners or members of the organization cannot access this view.
    Only owners can update organization details.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        object_label (str): The object label for the response.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Define the permission classes - require authentication
    permission_classes = [IsAuthenticated]

    # Define the object label
    object_label = "organization"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the organization detail view.

        This method handles exceptions for the organization detail view.

        Args:
            exc: The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return custom format for authentication errors
        if isinstance(exc, (AuthenticationFailed, TokenError)):
            return Response(
                {"error": str(exc)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Return the exception as a standard error
        return Response(
            {"error": str(exc)},
            status=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        )

    # Define the schema
    @extend_schema(
        tags=["Organizations"],
        summary="Get organization details.",
        description="""
        Retrieves the details of an organization.
        The authenticated user must be either the owner or a member of the organization.
        """,
        responses={
            status.HTTP_200_OK: OrganizationDetailResponseSerializer,
            status.HTTP_404_NOT_FOUND: OrganizationNotFoundResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def get(self, request: Request, organization_id: str) -> Response:
        """Get organization details.

        This method retrieves the details of an organization.
        The user must be the owner or a member of the organization.

        Args:
            request (Request): The HTTP request object.
            organization_id (str): The ID of the organization.

        Returns:
            Response: The HTTP response object.
        """

        try:
            # Get the organization by ID
            organization = Organization.objects.get(id=organization_id)

            # Check if the user is the owner or a member of the organization
            if (
                request.user != organization.owner
                and request.user not in organization.members.all()
            ):
                # Return 404 Not Found if the user is not the owner or a member
                return Response(
                    {
                        "error": "Organization not found or you don't have permission to view this organization.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Serialize the organization for the response body
            response_serializer = OrganizationSerializer(organization)

            # Return 200 OK with the serialized organization data
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK,
            )

        except Organization.DoesNotExist:
            # Return 404 Not Found if the organization doesn't exist
            return Response(
                {
                    "error": "Organization not found or you don't have permission to view this organization.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    # Define the schema
    @extend_schema(
        tags=["Organizations"],
        summary="Update organization details.",
        description="""
        Updates details of an organization.
        Only the owner of the organization can update its details.
        """,
        request=OrganizationUpdateSerializer,
        responses={
            status.HTTP_200_OK: OrganizationUpdateSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: OrganizationUpdateErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: OrganizationNotFoundResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def patch(self, request: Request, organization_id: str) -> Response:
        """Update organization details.

        This method updates the details of an organization.
        Only the owner can update organization details.

        Args:
            request (Request): The HTTP request object.
            organization_id (str): The ID of the organization.

        Returns:
            Response: The HTTP response object.
        """
        try:
            # Get the organization by ID
            organization = Organization.objects.get(id=organization_id)

            # Check if the user is the owner of the organization
            if request.user != organization.owner:
                # Return 404 Not Found if the user is not the owner
                return Response(
                    {
                        "error": "Organization not found or you are not the owner.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Create a serializer with the organization and request data
            serializer = OrganizationUpdateSerializer(
                organization,
                data=request.data,
                partial=True,
                context={"request": request},
            )

            # Validate the serializer
            if serializer.is_valid():
                # Save the updated organization
                updated_organization = serializer.save()

                # Serialize the updated organization for the response
                response_serializer = OrganizationSerializer(updated_organization)

                # Return 200 OK with the updated organization data
                return Response(
                    response_serializer.data,
                    status=status.HTTP_200_OK,
                )

            # Return 400 Bad Request with validation errors
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Organization.DoesNotExist:
            # Return 404 Not Found if the organization doesn't exist
            return Response(
                {
                    "error": "Organization not found or you are not the owner.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )


# Organization List View
class OrganizationListView(APIView):
    """Organization list view.

    This view allows authenticated users to list all organizations they own.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        object_label (str): The object label for the response.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Define the permission classes - require authentication
    permission_classes = [IsAuthenticated]

    # Define the object label
    object_label = "organizations"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the organization list view.

        This method handles exceptions for the organization list view.

        Args:
            exc: The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return custom format for authentication errors
        if isinstance(exc, (AuthenticationFailed, TokenError)):
            return Response(
                {"error": str(exc)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Return the exception as a standard error
        return Response(
            {"error": str(exc)},
            status=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        )

    # Define the schema
    @extend_schema(
        tags=["Organizations"],
        summary="List user's owned organizations.",
        description="""
        Lists all organizations owned by the authenticated user.
        """,
        responses={
            status.HTTP_200_OK: OrganizationListResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        """List user's owned organizations.

        This method retrieves all organizations owned by the authenticated user.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object containing the list of organizations.
        """

        # Get all organizations owned by the user
        organizations = Organization.objects.filter(owner=request.user)

        # Serialize the organizations for the response body
        response_serializer = OrganizationSerializer(organizations, many=True)

        # Return 200 OK with the serialized organizations data
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


# Organization Member List View
class OrganizationMemberListView(APIView):
    """Organization member list view.

    This view allows authenticated users to list all organizations they are a member of.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        object_label (str): The object label for the response.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Define the permission classes - require authentication
    permission_classes = [IsAuthenticated]

    # Define the object label
    object_label = "organizations"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the organization member list view.

        This method handles exceptions for the organization member list view.

        Args:
            exc: The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return custom format for authentication errors
        if isinstance(exc, (AuthenticationFailed, TokenError)):
            return Response(
                {"error": str(exc)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Return the exception as a standard error
        return Response(
            {"error": str(exc)},
            status=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        )

    # Define the schema
    @extend_schema(
        tags=["Organizations"],
        summary="List organizations where user is a member.",
        description="""
        Lists all organizations where the authenticated user is a member.
        This includes organizations the user owns and organizations they have been added to as a member.
        """,
        responses={
            status.HTTP_200_OK: OrganizationMembershipListResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        """List organizations where user is a member.

        This method retrieves all organizations where the authenticated user is a member.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object containing the list of organizations.
        """

        # Get all organizations where the user is a member
        member_organizations = request.user.organizations.all()

        # Get all organizations owned by the user
        owned_organizations = Organization.objects.filter(owner=request.user)

        # Combine the two querysets without duplicates
        organizations = (member_organizations | owned_organizations).distinct()

        # Serialize the organizations for the response body
        response_serializer = OrganizationSerializer(organizations, many=True)

        # Return 200 OK with the serialized organizations data
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


# Consolidated Organization Member Add View
class OrganizationMemberAddView(APIView):
    """Organization member add view.

    Allows organization owners to add a member using the user's ID, email, or username.
    Exactly one identifier must be provided in the request body.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        object_label (str): The object label for the response.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Define the permission classes - require authentication
    permission_classes = [IsAuthenticated]

    # Define the object label
    object_label = "organization"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the organization member add view.

        This method handles exceptions for the organization member add view.

        Args:
            exc: The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return custom format for authentication errors
        if isinstance(exc, (AuthenticationFailed, TokenError)):
            # Return 401 Unauthorized if the authentication failed
            return Response(
                {"error": str(exc)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Return the exception as a standard error
        return Response(
            {"error": str(exc)},
            status=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        )

    # Define the schema
    @extend_schema(
        tags=["Organizations"],
        summary="Add a member to an organization.",
        description="""
        Adds a user to an organization as a member using the user's ID, email, or username.
        Exactly one identifier (user_id, email, or username) must be provided.
        The authenticated user must be the owner of the organization.
        """,
        request=OrganizationMemberAddSerializer,
        responses={
            status.HTTP_200_OK: OrganizationMemberAddSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: OrganizationMemberAddErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: OrganizationNotFoundResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def post(self, request: Request, organization_id: str) -> Response:
        """Add a member to an organization.

        This method adds a user to an organization as a member using the user's ID, email, or username.

        Args:
            request (Request): The HTTP request object.
            organization_id (str): The ID of the organization.

        Returns:
            Response: The HTTP response object.
        """

        try:
            # Get the organization by ID and check if the user is the owner
            organization = Organization.objects.get(
                id=organization_id,
                owner=request.user,
            )

        except Organization.DoesNotExist:
            # Return 404 Not Found if the organization doesn't exist or user is not the owner
            return Response(
                {
                    "error": "Organization not found or you are not the owner.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Create a serializer for adding a member, passing the organization in context
        serializer = OrganizationMemberAddSerializer(
            data=request.data,
            context={"organization": organization},
        )

        # Validate the serializer
        if serializer.is_valid():
            # Get the validated user from the serializer
            user_to_add = serializer.get_user()

            # Add the user to the organization
            organization.add_member(user_to_add)

            # Serialize the updated organization for the response body
            response_serializer = OrganizationSerializer(organization)

            # Return 200 OK with the serialized organization data
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK,
            )

        # Return 400 Bad Request with validation errors
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# Consolidated Organization Member Remove View
class OrganizationMemberRemoveView(APIView):
    """Organization member remove view.

    Allows organization owners to remove a member using the user's ID, email, or username.
    Exactly one identifier must be provided in the request body.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        object_label (str): The object label for the response.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Define the permission classes - require authentication
    permission_classes = [IsAuthenticated]

    # Define the object label
    object_label = "organization"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the organization member remove view.

        This method handles exceptions for the organization member remove view.

        Args:
            exc: The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return custom format for authentication errors
        if isinstance(exc, (AuthenticationFailed, TokenError)):
            # Return 401 Unauthorized if the authentication failed
            return Response(
                {"error": str(exc)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Return the exception as a standard error
        return Response(
            {"error": str(exc)},
            status=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        )

    # Define the schema
    @extend_schema(
        tags=["Organizations"],
        summary="Remove a member from an organization.",
        description="""
        Removes a user from an organization using the user's ID, email, or username.
        Exactly one identifier (user_id, email, or username) must be provided.
        The authenticated user must be the owner of the organization. The owner cannot be removed.
        """,
        request=OrganizationMemberRemoveSerializer,
        responses={
            status.HTTP_200_OK: OrganizationMemberRemoveSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: OrganizationMemberRemoveErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: OrganizationNotFoundResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def post(self, request: Request, organization_id: str) -> Response:
        """Remove a member from an organization.

        This method removes a user from an organization using the user's ID, email, or username.

        Args:
            request (Request): The HTTP request object.
            organization_id (str): The ID of the organization.

        Returns:
            Response: The HTTP response object.
        """

        try:
            # Get the organization by ID and check if the user is the owner
            organization = Organization.objects.get(
                id=organization_id,
                owner=request.user,
            )

        except Organization.DoesNotExist:
            # Return 404 Not Found if the organization doesn't exist or user is not the owner
            return Response(
                {
                    "error": "Organization not found or you are not the owner.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Create a serializer for removing a member, passing the organization in context
        serializer = OrganizationMemberRemoveSerializer(
            data=request.data,
            context={"organization": organization},
        )

        # Validate the serializer
        if serializer.is_valid():
            # Get the validated user from the serializer
            user_to_remove = serializer.get_user()

            # Remove the user from the organization
            organization.remove_member(user_to_remove)

            # Serialize the updated organization for the response body
            response_serializer = OrganizationSerializer(organization)

            # Return 200 OK with the serialized organization data
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK,
            )

        # Return 400 Bad Request with validation errors
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# Organization Ownership Transfer Initialization View
class OrganizationOwnershipTransferInitView(APIView):
    """Organization ownership transfer initialization view.

    This view allows organization owners to initiate ownership transfers.
    A new owner is specified using the user's ID, email, or username.
    The new owner must be a member of the organization.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        object_label (str): The object label for the response.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Define the permission classes - require authentication
    permission_classes = [IsAuthenticated]

    # Define the object label
    object_label = "transfer"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the organization ownership transfer initialization view.

        This method handles exceptions for the organization ownership transfer initialization view.

        Args:
            exc: The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return custom format for authentication errors
        if isinstance(exc, (AuthenticationFailed, TokenError)):
            # Return 401 Unauthorized if the authentication failed
            return Response(
                {"error": str(exc)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Return the exception as a standard error
        return Response(
            {"error": str(exc)},
            status=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        )

    # Define the schema
    @extend_schema(
        tags=["Organizations"],
        summary="Initialize organization ownership transfer.",
        description="""
        Initializes an ownership transfer for an organization.
        Only the current owner can initiate a transfer, and the new owner must be a member of the organization.
        Exactly one identifier (user_id, email, or username) must be provided to identify the new owner.
        The transfer request will expire after 72 hours if not accepted or rejected.
        If an expired transfer request exists, it will be updated.
        """,
        request=OrganizationOwnershipTransferInitSerializer,
        responses={
            status.HTTP_201_CREATED: OrganizationOwnershipTransferInitSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: OrganizationOwnershipTransferInitErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: OrganizationNotFoundResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def post(self, request: Request, organization_id: str) -> Response:
        """Initialize organization ownership transfer.

        This method initializes an ownership transfer for an organization.
        Only the current owner can initiate a transfer, and the new owner must be a member of the organization.

        Args:
            request (Request): The HTTP request object.
            organization_id (str): The ID of the organization.

        Returns:
            Response: The HTTP response object.
        """

        # Try to get the organization by ID
        try:
            # Get the organization
            organization = Organization.objects.get(id=organization_id)

        except Organization.DoesNotExist:
            # Return 404 Not Found if the organization doesn't exist
            return Response(
                {"error": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the user is the owner of the organization
        if organization.owner != request.user:
            # Return 404 Not Found if the user is not the owner
            return Response(
                {"error": "Organization not found or you don't have permission."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Create the serializer with the organization in the context
        serializer = OrganizationOwnershipTransferInitSerializer(
            data=request.data,
            context={"request": request, "organization": organization},
        )

        # Validate the serializer
        if serializer.is_valid():
            # Get the new owner
            new_owner = serializer.get_user()

            # Check if there's an active transfer for this organization
            active_transfer = OrganizationOwnershipTransfer.get_active_transfer(
                organization,
            )
            if active_transfer:
                # Return an error if there's already an active transfer
                return Response(
                    {
                        "errors": {
                            "non_field_errors": [
                                "There is already an active ownership transfer for this organization.",
                            ],
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if there's an expired transfer that hasn't been marked as expired yet
            expired_transfer = OrganizationOwnershipTransfer.get_expired_transfer(
                organization,
            )
            if expired_transfer:
                # Delete the expired transfer
                expired_transfer.delete()
                expired_transfer = None

            # Calculate the expiration time (72 hours from now)
            expiration_time = timezone.now() + timezone.timedelta(
                hours=OrganizationOwnershipTransfer.DEFAULT_EXPIRATION_HOURS,
            )

            # Create a new transfer request
            transfer = OrganizationOwnershipTransfer.objects.create(
                organization=organization,
                current_owner=request.user,
                new_owner=new_owner,
                expiration_time=expiration_time,
            )

            # Get scheme and domain from settings
            scheme = settings.ACTIVATION_SCHEME
            domain_part = settings.ACTIVATION_DOMAIN

            # Construct full accept URL
            relative_accept_path = reverse(
                "organization:organization-ownership-transfer-accept",
                kwargs={"transfer_id": transfer.id},
            )
            accept_url = f"{scheme}://{domain_part}{relative_accept_path}"

            # Construct full reject URL
            relative_reject_path = reverse(
                "organization:organization-ownership-transfer-reject",
                kwargs={"transfer_id": transfer.id},
            )
            reject_url = f"{scheme}://{domain_part}{relative_reject_path}"

            # Send an email to the new owner with accept and reject links
            context = {
                "current_owner": request.user,
                "new_owner": new_owner,
                "organization": organization,
                "transfer_id": transfer.id,
                "expiration_time": transfer.expiration_time,
                "accept_url": accept_url,
                "reject_url": reject_url,
                "domain_part": domain_part,
            }

            # Send the email to the new owner
            send_templated_mail(
                template_name="organization/email/ownership_transfer_request.html",
                subject=f"Ownership Transfer Request for {organization.name}",
                context=context,
                recipient_list=[new_owner.email],
            )

            # Create a cancel URL for the current owner
            relative_cancel_path = reverse(
                "organization:organization-ownership-transfer-cancel",
                kwargs={"organization_id": organization.id},
            )
            cancel_url = f"{scheme}://{domain_part}{relative_cancel_path}"

            # Send a confirmation email to the current owner
            current_owner_context = {
                "current_owner": request.user,
                "new_owner": new_owner,
                "organization": organization,
                "transfer_id": transfer.id,
                "expiration_time": transfer.expiration_time,
                "domain_part": domain_part,
                "cancel_url": cancel_url,
            }

            # Send the email to the current owner
            send_templated_mail(
                template_name="organization/email/ownership_transfer_initiated.html",
                subject=f"You Initiated an Ownership Transfer for {organization.name}",
                context=current_owner_context,
                recipient_list=[request.user.email],
            )

            # Serialize the transfer for the response
            response_serializer = OrganizationOwnershipTransferInitResponseSerializer(
                transfer,
            )

            # Return 201 Created with the transfer data
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED,
            )

        # Return 400 Bad Request with validation errors
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# Organization Ownership Transfer Accept View
class OrganizationOwnershipTransferAcceptView(APIView):
    """Organization ownership transfer accept view.

    This view allows the new owner to accept an ownership transfer.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        object_label (str): The object label for the response.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Define the permission classes - require authentication
    permission_classes = [IsAuthenticated]

    # Define the object label
    object_label = "organization"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the organization ownership transfer accept view.

        This method handles exceptions for the organization ownership transfer accept view.

        Args:
            exc: The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return custom format for authentication errors
        if isinstance(exc, (AuthenticationFailed, TokenError)):
            # Return 401 Unauthorized if the authentication failed
            return Response(
                {"error": str(exc)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Return the exception as a standard error
        return Response(
            {"error": str(exc)},
            status=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        )

    # Define the schema
    @extend_schema(
        tags=["Organizations"],
        summary="Accept organization ownership transfer.",
        description="""
        Accepts an ownership transfer for an organization.
        Only the new owner can accept the transfer.
        The transfer must be active (not expired, not already accepted, not rejected, not cancelled).
        """,
        responses={
            status.HTTP_200_OK: OrganizationOwnershipTransferStatusSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: OrganizationOwnershipTransferStatusErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: OrganizationOwnershipTransferNotFoundResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def get(self, request: Request, transfer_id: str) -> Response:
        """Accept organization ownership transfer.

        This method accepts an ownership transfer for an organization.
        Only the new owner can accept the transfer.

        Args:
            request (Request): The HTTP request object.
            transfer_id (str): The ID of the transfer.

        Returns:
            Response: The HTTP response object.
        """

        # Try to get the transfer by ID
        try:
            # Get the transfer
            transfer = OrganizationOwnershipTransfer.objects.get(id=transfer_id)

        except OrganizationOwnershipTransfer.DoesNotExist:
            # Return 404 Not Found if the transfer doesn't exist
            return Response(
                {
                    "error": "Organization ownership transfer not found or you don't have permission.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the user is the new owner
        if transfer.new_owner != request.user:
            # Return 404 Not Found if the user is not the new owner
            return Response(
                {
                    "error": "Organization ownership transfer not found or you don't have permission.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the transfer is active
        if not transfer.is_active:
            # Return 400 Bad Request if the transfer is not active
            return Response(
                {"error": "The ownership transfer is no longer active."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Accept the transfer (this will update the organization's owner)
            transfer.accept_transfer()

            # Get domain part for the email footer
            domain_part = settings.ACTIVATION_DOMAIN

            # Send confirmation emails to both owners
            # Email to previous owner
            previous_owner_context = {
                "previous_owner": transfer.current_owner,
                "new_owner": transfer.new_owner,
                "organization": transfer.organization,
                "domain_part": domain_part,
            }
            send_templated_mail(
                template_name="organization/email/ownership_transfer_accepted_previous_owner.html",
                subject=f"Ownership Transfer Accepted for {transfer.organization.name}",
                context=previous_owner_context,
                recipient_list=[transfer.current_owner.email],
            )

            # Email to new owner
            new_owner_context = {
                "previous_owner": transfer.current_owner,
                "new_owner": transfer.new_owner,
                "organization": transfer.organization,
                "domain_part": domain_part,
            }
            send_templated_mail(
                template_name="organization/email/ownership_transfer_accepted_new_owner.html",
                subject=f"You Are Now the Owner of {transfer.organization.name}",
                context=new_owner_context,
                recipient_list=[transfer.new_owner.email],
            )

            # Return 200 OK with a success message
            return Response(
                {"message": "Ownership transfer accepted successfully."},
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            # Return 400 Bad Request with the error
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


# Organization Ownership Transfer Reject View
class OrganizationOwnershipTransferRejectView(APIView):
    """Organization ownership transfer reject view.

    This view allows the new owner to reject an ownership transfer.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        object_label (str): The object label for the response.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Define the permission classes - require authentication
    permission_classes = [IsAuthenticated]

    # Define the object label
    object_label = "organization"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the organization ownership transfer reject view.

        This method handles exceptions for the organization ownership transfer reject view.

        Args:
            exc: The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return custom format for authentication errors
        if isinstance(exc, (AuthenticationFailed, TokenError)):
            # Return 401 Unauthorized if the authentication failed
            return Response(
                {"error": str(exc)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Return the exception as a standard error
        return Response(
            {"error": str(exc)},
            status=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        )

    # Define the schema
    @extend_schema(
        tags=["Organizations"],
        summary="Reject organization ownership transfer.",
        description="""
        Rejects an ownership transfer for an organization.
        Only the new owner can reject the transfer.
        The transfer must be active (not expired, not already accepted, not rejected, not cancelled).
        """,
        responses={
            status.HTTP_200_OK: OrganizationOwnershipTransferStatusSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: OrganizationOwnershipTransferStatusErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: OrganizationOwnershipTransferNotFoundResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def get(self, request: Request, transfer_id: str) -> Response:
        """Reject organization ownership transfer.

        This method rejects an ownership transfer for an organization.
        Only the new owner can reject the transfer.

        Args:
            request (Request): The HTTP request object.
            transfer_id (str): The ID of the transfer.

        Returns:
            Response: The HTTP response object.
        """

        # Try to get the transfer by ID
        try:
            # Get the transfer
            transfer = OrganizationOwnershipTransfer.objects.get(id=transfer_id)

        except OrganizationOwnershipTransfer.DoesNotExist:
            # Return 404 Not Found if the transfer doesn't exist
            return Response(
                {
                    "error": "Organization ownership transfer not found or you don't have permission.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the user is the new owner
        if transfer.new_owner != request.user:
            # Return 404 Not Found if the user is not the new owner
            return Response(
                {
                    "error": "Organization ownership transfer not found or you don't have permission.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the transfer is active
        if not transfer.is_active:
            # Return 400 Bad Request if the transfer is not active
            return Response(
                {"error": "The ownership transfer is no longer active."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Reject the transfer
            transfer.reject_transfer()

            # Get domain part for the email footer
            domain_part = settings.ACTIVATION_DOMAIN

            # Send notification email to the current owner
            context = {
                "current_owner": transfer.current_owner,
                "new_owner": transfer.new_owner,
                "organization": transfer.organization,
                "domain_part": domain_part,
            }
            send_templated_mail(
                template_name="organization/email/ownership_transfer_rejected.html",
                subject=f"Ownership Transfer Rejected for {transfer.organization.name}",
                context=context,
                recipient_list=[transfer.current_owner.email],
            )

            # Return 200 OK with a success message
            return Response(
                {"message": "Ownership transfer rejected successfully."},
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            # Return 400 Bad Request with the error
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


# Organization Ownership Transfer Cancel View
class OrganizationOwnershipTransferCancelView(APIView):
    """Organization ownership transfer cancel view.

    This view allows the current owner to cancel an ownership transfer.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        object_label (str): The object label for the response.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Define the permission classes - require authentication
    permission_classes = [IsAuthenticated]

    # Define the object label
    object_label = "organization"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the organization ownership transfer cancel view.

        This method handles exceptions for the organization ownership transfer cancel view.

        Args:
            exc: The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return custom format for authentication errors
        if isinstance(exc, (AuthenticationFailed, TokenError)):
            # Return 401 Unauthorized if the authentication failed
            return Response(
                {"error": str(exc)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Return the exception as a standard error
        return Response(
            {"error": str(exc)},
            status=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        )

    # Define the schema
    @extend_schema(
        tags=["Organizations"],
        summary="Cancel organization ownership transfer.",
        description="""
        Cancels an ownership transfer for an organization.
        Only the current owner can cancel the transfer.
        The transfer must be active (not expired, not already accepted, not rejected, not cancelled).
        """,
        responses={
            status.HTTP_200_OK: OrganizationOwnershipTransferStatusSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: OrganizationOwnershipTransferStatusErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: OrganizationOwnershipTransferNotFoundResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def get(self, request: Request, organization_id: str) -> Response:
        """Cancel organization ownership transfer.

        This method cancels an ownership transfer for an organization.
        Only the current owner can cancel the transfer.

        Args:
            request (Request): The HTTP request object.
            organization_id (str): The ID of the organization.

        Returns:
            Response: The HTTP response object.
        """

        # Try to get the organization by ID
        try:
            # Get the organization
            organization = Organization.objects.get(id=organization_id)

        except Organization.DoesNotExist:
            # Return 404 Not Found if the organization doesn't exist
            return Response(
                {"error": "Organization not found or you don't have permission."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the user is the owner of the organization
        if organization.owner != request.user:
            # Return 404 Not Found if the user is not the owner
            return Response(
                {"error": "Organization not found or you don't have permission."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get the active transfer for this organization
        transfer = OrganizationOwnershipTransfer.get_active_transfer(organization)
        if not transfer:
            # Return 400 Bad Request if there's no active transfer
            return Response(
                {"error": "No active ownership transfer found for this organization."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Cancel the transfer
            transfer.cancel_transfer()

            # Get domain part for the email footer
            domain_part = settings.ACTIVATION_DOMAIN

            # Send notification email to the new owner
            context = {
                "current_owner": transfer.current_owner,
                "new_owner": transfer.new_owner,
                "organization": transfer.organization,
                "domain_part": domain_part,
            }
            send_templated_mail(
                template_name="organization/email/ownership_transfer_cancelled.html",
                subject=f"Ownership Transfer Cancelled for {transfer.organization.name}",
                context=context,
                recipient_list=[transfer.new_owner.email],
            )

            # Return 200 OK with a success message
            return Response(
                {"message": "Ownership transfer cancelled successfully."},
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            # Return 400 Bad Request with the error
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
