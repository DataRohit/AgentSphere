# Third-party imports
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# Project imports
from apps.common.renderers import GenericJSONRenderer
from apps.organization.models import Organization
from apps.organization.serializers import OrganizationCreateErrorResponseSerializer
from apps.organization.serializers import OrganizationCreateSerializer
from apps.organization.serializers import OrganizationCreateSuccessResponseSerializer
from apps.organization.serializers import OrganizationLogoErrorResponseSerializer
from apps.organization.serializers import OrganizationLogoNotFoundResponseSerializer
from apps.organization.serializers import OrganizationLogoSerializer
from apps.organization.serializers import OrganizationLogoSuccessResponseSerializer
from apps.organization.serializers import OrganizationSerializer


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
