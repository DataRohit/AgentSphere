# Third-party imports
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError

# Local application imports
from apps.common.renderers import GenericJSONRenderer
from apps.organization.models import Organization
from apps.organization.serializers import (
    OrganizationAuthErrorResponseSerializer,
    OrganizationMemberAddErrorResponseSerializer,
    OrganizationMemberAddSerializer,
    OrganizationMemberAddSuccessResponseSerializer,
    OrganizationNotFoundResponseSerializer,
    OrganizationSerializer,
)

# Get the User model
User = get_user_model()


# Consolidated Organization Member Add View
class OrganizationMemberAddView(APIView):
    """Organization member add view.

    Allows organization owners to add a member using the user's ID, email, or username.
    Exactly one identifier must be provided in the request body.
    An organization can have a maximum of 8 members (including the owner).

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
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the organization member add view.

        This method handles exceptions for the organization member add view.

        Args:
            exc (Exception): The exception that occurred.

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
        description=f"""
        Adds a user to an organization as a member using the user's ID, email, or username.
        Exactly one identifier (user_id, email, or username) must be provided.
        The authenticated user must be the owner of the organization.
        An organization can have a maximum of {Organization.MAX_MEMBERS_PER_ORGANIZATION} members (including the owner).
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
        An organization can have a maximum of 8 members (including the owner).

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
            try:
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

            except ValueError as e:
                # Return 400 Bad Request with member limit error
                return Response(
                    {"errors": {"non_field_errors": [str(e)]}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Return 400 Bad Request with validation errors
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
