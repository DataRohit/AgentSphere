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
from apps.llms.serializers import (
    LLMAuthErrorResponseSerializer,
    LLMCreateErrorResponseSerializer,
    LLMCreateSerializer,
    LLMCreateSuccessResponseSerializer,
    LLMSerializer,
)

# Get the User model
User = get_user_model()


# LLM creation view
class LLMCreateView(APIView):
    """LLM creation view.

    This view allows authenticated users to create new LLM configurations within an organization.
    The user must be a member of the organization to create LLMs within it.

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
        """Handle exceptions for the LLM creation view.

        This method handles exceptions for the LLM creation view.

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

        # Return the exception as a standard error
        return Response(
            {"error": str(exc)},
            status=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        )

    # Define the schema for the POST view
    @extend_schema(
        tags=["LLMs"],
        summary="Create a new LLM configuration.",
        description="""
        Creates a new LLM configuration within an organization with the authenticated user as the creator.
        The user must be a member of the specified organization.
        For Gemini API type, an API key is required.
        """,
        request=LLMCreateSerializer,
        responses={
            status.HTTP_201_CREATED: LLMCreateSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: LLMCreateErrorResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: LLMAuthErrorResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        """Create a new LLM configuration.

        This method creates a new LLM configuration with the authenticated user as the creator
        within the specified organization.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Create a new LLM instance
        serializer = LLMCreateSerializer(
            data=request.data,
            context={"request": request},
        )

        # Validate the serializer
        if serializer.is_valid():
            # Save the LLM instance
            llm = serializer.save()

            # Serialize the created LLM for the response body
            response_serializer = LLMSerializer(llm)

            # Return a successful response with the serialized LLM data
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED,
            )

        # Return an error response with validation errors
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
