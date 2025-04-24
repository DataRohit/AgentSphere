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
    OrganizationMemberRemoveErrorResponseSerializer,
    OrganizationMemberRemoveSerializer,
    OrganizationMemberRemoveSuccessResponseSerializer,
    OrganizationNotFoundResponseSerializer,
)
from apps.organization.tasks import (
    delete_user_agents_in_organization,
    delete_user_llms_in_organization,
)

# Get the User model
User = get_user_model()


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
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the organization member remove view.

        This method handles exceptions for the organization member remove view.

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

            # Delete the user's agents in the organization using Celery task
            delete_user_agents_in_organization.delay(
                user_id=str(user_to_remove.id),
                organization_id=str(organization.id),
            )

            # Delete the user's LLMs in the organization using Celery task
            delete_user_llms_in_organization.delay(
                user_id=str(user_to_remove.id),
                organization_id=str(organization.id),
            )

            # Return 200 OK with the serialized organization data
            return Response(
                {
                    "message": "Member removed successfully.",
                },
                status=status.HTTP_200_OK,
            )

        # Return 400 Bad Request with validation errors
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
