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
    OrganizationDeleteStatusSuccessResponseSerializer,
    OrganizationDetailResponseSerializer,
    OrganizationNotFoundResponseSerializer,
    OrganizationSerializer,
    OrganizationUpdateErrorResponseSerializer,
    OrganizationUpdateSerializer,
    OrganizationUpdateSuccessResponseSerializer,
)

# Get the User model
User = get_user_model()


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
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the organization detail view.

        This method handles exceptions for the organization detail view.

        Args:
            exc (Exception): The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return custom format for authentication errors
        if isinstance(exc, (AuthenticationFailed, TokenError)):
            # Return the error response
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
            if request.user != organization.owner and request.user not in organization.members.all():
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

    # Define the schema
    @extend_schema(
        tags=["Organizations"],
        summary="Delete an organization.",
        description="""
        Deletes an organization.
        Only the owner of the organization can delete it.
        This operation cannot be undone.
        """,
        responses={
            status.HTTP_200_OK: OrganizationDeleteStatusSuccessResponseSerializer,
            status.HTTP_404_NOT_FOUND: OrganizationNotFoundResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: OrganizationAuthErrorResponseSerializer,
        },
    )
    def delete(self, request: Request, organization_id: str) -> Response:
        """Delete an organization.

        This method deletes an organization.
        Only the owner can delete an organization.

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

            # Store organization name before deletion for the response message
            organization_name = organization.name

            # Delete the organization
            organization.delete()

            # Return 200 OK with a success message
            return Response(
                {
                    "message": f"Organization '{organization_name}' was successfully deleted.",
                },
                status=status.HTTP_200_OK,
            )

        except Organization.DoesNotExist:
            # Return 404 Not Found if the organization doesn't exist
            return Response(
                {
                    "error": "Organization not found or you are not the owner.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
