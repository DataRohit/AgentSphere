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
    OrganizationLeaveErrorResponseSerializer,
    OrganizationLeaveSuccessResponseSerializer,
    OrganizationNotFoundResponseSerializer,
    OrganizationNotMemberResponseSerializer,
)
from apps.organization.tasks import (
    delete_user_agents_in_organization,
    delete_user_llms_in_organization,
)

# Get the User model
User = get_user_model()


# Organization Leave View
class OrganizationLeaveView(APIView):
    """Organization leave view.

    Allows users to leave an organization they are a member of.
    The owner of an organization cannot leave - they must transfer ownership first.

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
        """Handle exceptions for the organization leave view.

        This method handles exceptions for the organization leave view.

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
        summary="Leave an organization.",
        description="""
        Allows a user to leave an organization they are a member of.
        The owner of an organization cannot leave - they must transfer ownership first.
        """,
        responses={
            status.HTTP_200_OK: OrganizationLeaveSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: OrganizationLeaveErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: OrganizationNotMemberResponseSerializer,
            status.HTTP_404_NOT_FOUND: OrganizationNotFoundResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def delete(self, request: Request, organization_id: str) -> Response:
        """Leave an organization.

        This method allows a user to leave an organization they are a member of.
        The owner of an organization cannot leave - they must transfer ownership first.

        Args:
            request (Request): The HTTP request object.
            organization_id (str): The ID of the organization.

        Returns:
            Response: The HTTP response object.
        """

        try:
            # Get the organization by ID
            organization = Organization.objects.get(id=organization_id)

        except Organization.DoesNotExist:
            # Return 404 Not Found if the organization doesn't exist
            return Response(
                {
                    "error": "Organization not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get the current user
        user = request.user

        # Check if the user is the owner of the organization
        if user == organization.owner:
            # Return 400 Bad Request if the user is the owner
            return Response(
                {
                    "errors": {
                        "non_field_errors": [
                            "You are the owner of this organization. You must transfer ownership before leaving.",
                        ],
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the user is a member of the organization
        if user not in organization.members.all():
            # Return 403 Forbidden if the user is not a member
            return Response(
                {
                    "error": "You are not a member of this organization.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Remove the user from the organization
        organization.remove_member(user)

        # Delete the user's agents in the organization using Celery task
        delete_user_agents_in_organization.delay(
            user_id=str(user.id),
            organization_id=str(organization.id),
        )

        # Delete the user's LLMs in the organization using Celery task
        delete_user_llms_in_organization.delay(
            user_id=str(user.id),
            organization_id=str(organization.id),
        )

        # Return 200 OK with a success message
        return Response(
            {"message": "You have successfully left the organization."},
            status=status.HTTP_200_OK,
        )
