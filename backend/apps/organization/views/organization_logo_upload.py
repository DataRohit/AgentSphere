# Third-party imports
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.parsers import FormParser, MultiPartParser
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
    OrganizationLogoErrorResponseSerializer,
    OrganizationLogoNotFoundResponseSerializer,
    OrganizationLogoSerializer,
    OrganizationLogoSuccessResponseSerializer,
    OrganizationSerializer,
)

# Get the User model
User = get_user_model()


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
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the organization logo upload view.

        This method handles exceptions for the organization logo upload view.

        Args:
            exc (Exception): The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return custom format for authentication errors
        if isinstance(exc, (AuthenticationFailed, TokenError)):
            # Return 401 Unauthorized with the error message
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
