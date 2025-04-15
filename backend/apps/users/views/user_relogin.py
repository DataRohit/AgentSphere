# Third-party imports
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView

# Local application imports
from apps.users.serializers import (
    UserReloginErrorResponseSerializer,
    UserReloginResponseSerializer,
    UserReloginSerializer,
)


# User relogin view
class UserReloginView(TokenRefreshView):
    """User relogin view.

    This view handles refreshing JWT access tokens.
    It extends the TokenRefreshView to provide custom behavior.

    Attributes:
        serializer_class (TokenRefreshSerializer): The serializer class for token refresh.
        permission_classes (list): The permission classes for the view.
        authentication_classes (list): The authentication classes for the view.
    """

    # Define the serializer class
    serializer_class = UserReloginSerializer

    # Define the permission classes
    permission_classes = [AllowAny]

    # Explicitly set empty authentication classes
    authentication_classes = []

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the relogin view.

        This method handles exceptions for the relogin view.

        Args:
            exc: The exception that occurred.

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
        summary="Refresh JWT access token.",
        description="""
        Refreshes a JWT access token using a valid refresh token.
        Use this endpoint when the access token has expired.
        The new access token will be valid for 6 hours.
        """,
        request=UserReloginSerializer,
        responses={
            status.HTTP_200_OK: UserReloginResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: UserReloginErrorResponseSerializer,
        },
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        """Handle POST request for token refresh.

        This method refreshes a JWT access token using a valid refresh token.

        Args:
            request (Request): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response object containing only the access token.

        Raises:
            InvalidToken: If the refresh token is invalid.
            TokenError: If there is an error with the token.
        """

        # Validate the refresh token
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Return only the access token
        return Response(
            {
                "access": serializer.validated_data["access"],
            },
            status=status.HTTP_200_OK,
        )
