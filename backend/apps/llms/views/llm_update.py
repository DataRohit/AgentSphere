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
    LLMNotFoundResponseSerializer,
    LLMPermissionDeniedResponseSerializer,
    LLMSerializer,
    LLMUpdateErrorResponseSerializer,
    LLMUpdateSerializer,
    LLMUpdateSuccessResponseSerializer,
)

# Get the User model
User = get_user_model()


# LLM update view
class LLMUpdateView(APIView):
    """LLM update view.

    This view allows users to update their own LLM configurations.
    Only the user who created an LLM can update it.

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
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the LLM update view.

        This method handles exceptions for the LLM update view.

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
        summary="Update an existing LLM configuration.",
        description="""
        Updates an existing LLM configuration. Only the user who created the LLM can update it.
        All fields are optional - only the fields that need to be updated should be included.
        """,
        request=LLMUpdateSerializer,
        responses={
            status.HTTP_200_OK: LLMUpdateSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: LLMUpdateErrorResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: LLMAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: LLMPermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: LLMNotFoundResponseSerializer,
        },
    )
    def patch(self, request: Request, llm_id: str) -> Response:
        """Update an existing LLM configuration.

        This method updates an existing LLM configuration. Only the user who created the LLM can update it.

        Args:
            request (Request): The HTTP request object.
            llm_id (str): The ID of the LLM to update.

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
                    {
                        "error": "You do not have permission to update this LLM configuration.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Create serializer with the LLM and data
            serializer = LLMUpdateSerializer(llm, data=request.data, partial=True)

            # Validate the serializer
            if serializer.is_valid():
                # Save the updated LLM
                updated_llm = serializer.save()

                # Serialize the updated LLM for response
                response_serializer = LLMSerializer(updated_llm)

                # Return 200 OK with the updated LLM data
                return Response(
                    response_serializer.data,
                    status=status.HTTP_200_OK,
                )

            # Return 400 Bad Request with validation errors
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except LLM.DoesNotExist:
            # If the LLM doesn't exist, return a 404 error
            return Response(
                {"error": "LLM configuration not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
