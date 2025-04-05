# Third-party imports
from drf_spectacular.utils import extend_schema
from rest_framework import status
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
