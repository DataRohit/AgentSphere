# Third-party imports
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

# Local application imports
from apps.users.serializers import (
    UserLoginErrorResponseSerializer,
    UserLoginResponseSerializer,
    UserLoginSerializer,
)


# User login view
class UserLoginView(TokenObtainPairView):
    """User login view.

    This view handles user authentication and generates JWT tokens.
    It extends the TokenObtainPairView to provide custom token claims.

    Attributes:
        serializer_class (TokenObtainPairSerializer): The serializer class for token generation.
        permission_classes (list): The permission classes for the view.
        authentication_classes (list): The authentication classes for the view.
    """

    # Define the serializer class
    serializer_class = UserLoginSerializer

    # Define the permission classes
    permission_classes = [AllowAny]

    # Explicitly set empty authentication classes
    authentication_classes = []

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the login view.

        This method handles exceptions for the login view.

        Args:
            exc (Exception): The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return only the error field for errors
        return Response(
            {"error": str(exc)},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Define the schema
    @extend_schema(
        tags=["Users"],
        summary="Log in and get JWT tokens.",
        description="""
        Authenticates a user and returns JWT tokens for API access.
        The access token is valid for 6 hours and the refresh token for 24 hours.
        Use the access token for all authenticated API requests.
        """,
        request=UserLoginSerializer,
        responses={
            status.HTTP_200_OK: UserLoginResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: UserLoginErrorResponseSerializer,
        },
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        """Handle POST request for user login.

        This method authenticates a user and returns JWT tokens for API access.

        Args:
            request (Request): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response object.
        """

        # Call the parent class's post method
        return super().post(request, *args, **kwargs)
