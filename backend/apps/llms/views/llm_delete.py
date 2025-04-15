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
    LLMDeleteNotFoundResponseSerializer,
    LLMDeletePermissionDeniedResponseSerializer,
    LLMDeleteSuccessResponseSerializer,
    LLMHasAgentsResponseSerializer,
)

# Get the User model
User = get_user_model()


# LLM delete view
class LLMDeleteView(APIView):
    """LLM delete view.

    This view allows users to delete their own LLM configurations.
    Only the user who created an LLM can delete it.
    An LLM cannot be deleted if it is associated with any agents.

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
        """Handle exceptions for the LLM delete view.

        This method handles exceptions for the LLM delete view.

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

    # Define the schema
    @extend_schema(
        tags=["LLMs"],
        summary="Delete an existing LLM configuration.",
        description="""
        Deletes an existing LLM configuration. Only the user who created the LLM can delete it.
        An LLM cannot be deleted if it is associated with any agents.
        """,
        responses={
            status.HTTP_200_OK: LLMDeleteSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: LLMHasAgentsResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: LLMAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: LLMDeletePermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: LLMDeleteNotFoundResponseSerializer,
        },
    )
    def delete(self, request: Request, llm_id: str) -> Response:
        """Delete an existing LLM configuration.

        This method deletes an existing LLM configuration. Only the user who created the LLM can delete it.
        An LLM cannot be deleted if it is associated with any agents.

        Args:
            request (Request): The HTTP request object.
            llm_id (str): The ID of the LLM to delete.

        Returns:
            Response: The HTTP response object.

        Raises:
            NotFound: If the LLM doesn't exist.
            PermissionDenied: If the user isn't the creator of the LLM.
        """

        # Get the authenticated user
        user = request.user

        try:
            # Try to get the LLM
            llm = LLM.objects.get(id=llm_id)

            # Check if the user is the creator of the LLM
            if llm.user != user:
                # Return the error response
                return Response(
                    {"error": "You do not have permission to delete this LLM."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Check if the LLM is associated with any agents
            if llm.agents.exists():
                # Return the error response
                return Response(
                    {
                        "error": "Cannot delete LLM because it is associated with one or more agents.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Delete the LLM
            llm.delete()

            # Return 200 OK with success message
            return Response(
                {"message": "LLM deleted successfully."},
                status=status.HTTP_200_OK,
            )

        except LLM.DoesNotExist:
            # If the LLM doesn't exist, return a 404 error
            return Response(
                {"error": "LLM not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
