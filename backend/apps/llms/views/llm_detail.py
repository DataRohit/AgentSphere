# Third-party imports
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError

# Local application imports
from apps.common.renderers import GenericJSONRenderer
from apps.llms.models import LLM
from apps.llms.serializers import (
    LLMAuthErrorResponseSerializer,
    LLMDetailNotFoundResponseSerializer,
    LLMDetailPermissionDeniedResponseSerializer,
    LLMDetailSuccessResponseSerializer,
    LLMSerializer,
)

# Get the User model
User = get_user_model()


# LLM detail view
class LLMDetailView(APIView):
    """LLM detail view.

    This view allows authenticated users to retrieve LLM configuration details by ID.
    Users can only view LLM configurations they created/own.

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
    object_label = "llm"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the LLM detail view.

        This method handles exceptions for the LLM detail view.

        Args:
            exc: The exception that occurred.

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

        # Return custom format for permission errors
        if isinstance(exc, PermissionDenied):
            # Return the error response
            return Response(
                {"error": str(exc)},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Return custom format for not found errors
        if isinstance(exc, NotFound):
            # Return the error response
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Return the exception as a standard error
        return Response(
            {"error": str(exc)},
            status=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        )

    # Define the schema for the detail view
    @extend_schema(
        tags=["LLMs"],
        summary="Get LLM configuration details by ID.",
        description="""
        Retrieves the details of a specific LLM configuration by its ID.
        Users can only view LLM configurations they created/own.
        """,
        responses={
            status.HTTP_200_OK: LLMDetailSuccessResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: LLMAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: LLMDetailPermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: LLMDetailNotFoundResponseSerializer,
        },
    )
    def get(self, request: Request, llm_id: str) -> Response:
        """Get LLM configuration details by ID.

        This method retrieves the details of a specific LLM configuration by its ID.
        Access is granted if:
        - The LLM is owned/created by the user

        Args:
            request (Request): The HTTP request object.
            llm_id (str): The ID of the LLM to retrieve.

        Returns:
            Response: The HTTP response object with the LLM details.

        Raises:
            NotFound: If the LLM does not exist.
            PermissionDenied: If the user does not have permission to view the LLM.
        """

        # Get the authenticated user
        user = request.user

        try:
            # Try to get the LLM
            llm = LLM.objects.get(id=llm_id)

            # The LLM is owned/created by the user
            if user == llm.user:
                # Return the LLM details
                return Response(
                    LLMSerializer(llm).data,
                    status=status.HTTP_200_OK,
                )

            # If the access condition is not met, deny access
            return Response(
                {"error": "You do not have permission to view this LLM configuration."},
                status=status.HTTP_403_FORBIDDEN,
            )

        except LLM.DoesNotExist:
            # Return a 404 error
            return Response(
                {"error": "LLM configuration not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
