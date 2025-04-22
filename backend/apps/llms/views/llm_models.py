# Third-party imports
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
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
from apps.llms.models.choices import ApiType, GoogleGeminiModel
from apps.llms.serializers.llm_models import (
    LLMModelsAuthErrorResponseSerializer,
    LLMModelsInvalidApiTypeResponseSerializer,
    LLMModelsSuccessResponseSerializer,
    ModelInfoSerializer,
)

# Get the User model
User = get_user_model()


# LLM models view
class LLMModelsView(APIView):
    """LLM models view.

    This view allows authenticated users to retrieve the list of supported models
    for a specific API type.

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
    object_label = "models"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the LLM models view.

        This method handles exceptions for the LLM models view.

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

        # Call the parent handle_exception method for other exceptions
        return super().handle_exception(exc)

    # Define the schema for the models view
    @extend_schema(
        tags=["LLMs"],
        summary="Get supported models for a specific API type.",
        description="""
        Retrieves the list of supported models for the specified API type.
        Currently supports 'google' API type.
        """,
        responses={
            status.HTTP_200_OK: LLMModelsSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: LLMModelsInvalidApiTypeResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: LLMModelsAuthErrorResponseSerializer,
        },
    )
    def get(self, request: Request, api_type: str) -> Response:
        """Get supported models for a specific API type.

        This method retrieves the list of supported models for the specified API type.

        Args:
            request (Request): The HTTP request object.
            api_type (str): The API type to get models for.

        Returns:
            Response: The HTTP response object with the list of supported models.
        """

        # Check if the API type is valid
        if api_type not in [choice[0] for choice in ApiType.choices]:
            # Return 400 Bad Request if the API type is invalid
            return Response(
                {
                    "error": _("Invalid API type. Supported types: {}.").format(
                        ", ".join([choice[0] for choice in ApiType.choices]),
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the models for the specified API type
        if api_type == ApiType.GOOGLE:
            # Get the Google Gemini models
            models = [{"id": choice[0], "name": choice[1]} for choice in GoogleGeminiModel.choices]

        else:
            # Return an empty list for unsupported API types
            models = []

        # Serialize the models
        serializer = ModelInfoSerializer(models, many=True)

        # Return the serialized models
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
