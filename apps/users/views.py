# Third-party imports
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

# Project imports
from apps.common.renderers import GenericJSONRenderer
from apps.common.utils import send_templated_mail
from apps.users.models import UserActivationToken
from apps.users.serializers import ResendActivationEmailSerializer
from apps.users.serializers import ResendActivationErrorResponseSerializer
from apps.users.serializers import ResendActivationSuccessResponseSerializer
from apps.users.serializers import UserActivationForbiddenResponseSerializer
from apps.users.serializers import UserActivationSuccessResponseSerializer
from apps.users.serializers import UserCreateErrorResponseSerializer
from apps.users.serializers import UserCreateSerializer
from apps.users.serializers import UserCreateSuccessResponseSerializer
from apps.users.serializers import UserDeactivateErrorResponseSerializer
from apps.users.serializers import UserDeactivateSerializer
from apps.users.serializers import UserDeactivateSuccessResponseSerializer
from apps.users.serializers import UserDetailSerializer
from apps.users.serializers import UserLoginErrorResponseSerializer
from apps.users.serializers import UserLoginResponseSerializer
from apps.users.serializers import UserLoginSerializer
from apps.users.serializers import UserProfileErrorResponseSerializer
from apps.users.serializers import UserProfileResponseSerializer
from apps.users.serializers import UserProfileSerializer
from apps.users.serializers import UserProfileUpdateErrorResponseSerializer
from apps.users.serializers import UserProfileUpdateResponseSerializer
from apps.users.serializers import UserProfileUpdateSerializer
from apps.users.serializers import UserReloginErrorResponseSerializer
from apps.users.serializers import UserReloginResponseSerializer
from apps.users.serializers import UserReloginSerializer

# Get the user model
User = get_user_model()


# User creation view
class UserCreateView(APIView):
    """User creation view.

    This view allows users to create new accounts. The user will be inactive until activated via email.
    The user will be sent an email with a link to activate their account.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Disable authentication checks for this view
    authentication_classes = []

    # Define the permission classes
    permission_classes = [AllowAny]

    # Define the object label
    object_label = "user"

    # Define the schema
    @extend_schema(
        tags=["Users"],
        summary="Register a new user account.",
        description="""
        Creates a new user account. The user will be inactive until activated via email.
        The user will be sent an email with a link to activate their account.
        """,
        request=UserCreateSerializer,
        responses={
            status.HTTP_201_CREATED: UserCreateSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: UserCreateErrorResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        """Register a new user account.

        This view allows users to create new accounts. The user will be inactive until activated via email.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Create a new user instance
        serializer = UserCreateSerializer(data=request.data)

        # Validate the serializer
        if serializer.is_valid():
            # Save the user instance
            user = serializer.save()

            # Generate activation token and uid
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # Store the activation token in the database
            UserActivationToken.objects.create(
                user=user,
                uid=uid,
                token=token,
            )

            # Get scheme and domain from settings
            scheme = settings.ACTIVATION_SCHEME
            domain_part = settings.ACTIVATION_DOMAIN

            # Construct full activation URL
            relative_activation_path = reverse(
                "users:user-activation",
                kwargs={"uid": uid, "token": token},
            )
            activation_url = f"{scheme}://{domain_part}{relative_activation_path}"

            # Prepare email context including domain_part
            context = {
                "user": user,
                "activation_link": activation_url,
                "current_year": timezone.now().year,
                "domain_part": domain_part,
            }

            # Send activation email using utility function
            send_templated_mail(
                template_name="users/user_activation.html",
                subject="Activate Your Account",
                context=context,
                recipient_list=[user.email],
            )

            # Serialize the created user with detailed fields for the response body
            response_serializer = UserDetailSerializer(user)

            # Return 201 Created with the serialized user data
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        # Return 400 Bad Request with validation errors
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# Resend Activation Email View
class ResendActivationEmailView(APIView):
    """View to resend the activation email for an inactive user.

    Accepts an email address via POST request. If a matching inactive user is found,
    it generates a new activation token, updates the database, and resends the activation email.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Disable authentication checks for this view
    authentication_classes = []

    # Define the permission classes
    permission_classes = [AllowAny]

    # Define the object label
    object_label = "activation"

    # Define the schema
    @extend_schema(
        tags=["Users"],
        summary="Resend activation email.",
        description="""
        Resends the activation email to a user if their account is inactive.
        The user must be inactive to receive a new activation email.
        """,
        request=ResendActivationEmailSerializer,
        responses={
            status.HTTP_200_OK: ResendActivationSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: ResendActivationErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: ResendActivationErrorResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        """Handle POST request to resend activation email.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Validate the serializer
        serializer = ResendActivationEmailSerializer(data=request.data)

        # If the serializer is not valid
        if not serializer.is_valid():
            # Return 400 Bad Request with validation errors
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the email from the validated data
        email = serializer.validated_data["email"]

        try:
            # Get the user from the database
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            # Return 404 Not Found with an error message
            return Response(
                {"errors": {"email": ["User with this email does not exist."]}},
                status=status.HTTP_404_NOT_FOUND,
            )

        # If the user is already active
        if user.is_active:
            # Return 400 Bad Request with an error message
            return Response(
                {
                    "errors": {
                        "non_field_errors": ["This account is already active."],
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate new activation token and uid
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Use transaction.atomic for the database operation
        with transaction.atomic():
            # Update or create the activation token
            UserActivationToken.objects.update_or_create(
                user=user,
                defaults={"uid": uid, "token": token},
            )

        # Get scheme and domain from settings
        scheme = settings.ACTIVATION_SCHEME
        domain_part = settings.ACTIVATION_DOMAIN

        # Construct full activation URL
        relative_activation_path = reverse(
            "users:user-activation",
            kwargs={"uid": uid, "token": token},
        )
        activation_url = f"{scheme}://{domain_part}{relative_activation_path}"

        # Prepare email context
        context = {
            "user": user,
            "activation_link": activation_url,
            "current_year": timezone.now().year,
            "domain_part": domain_part,
        }

        # Send activation email
        send_templated_mail(
            template_name="users/user_activation.html",
            subject="Activate Your Account (Resent)",
            context=context,
            recipient_list=[user.email],
        )

        # Return success response
        return Response(
            {"message": "Activation email resent successfully."},
            status=status.HTTP_200_OK,
        )


# User activation view
class UserActivationView(APIView):
    """User activation view.

    This view allows users to activate their accounts using the activation link sent to their email.
    The view verifies the token in the database and activates the account if valid.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Disable authentication checks for this view
    authentication_classes = []

    # Define the permission classes
    permission_classes = [AllowAny]

    # Define the object label
    object_label = "activation"

    # Define the schema
    @extend_schema(
        tags=["Users"],
        summary="Activate a user account.",
        description="""
        Activates a user account using the UID and token from the activation link.
        The UID identifies the user, and the token verifies the activation request.
        The activation link is valid for 30 minutes and can only be used once.
        """,
        responses={
            status.HTTP_200_OK: UserActivationSuccessResponseSerializer,
            status.HTTP_403_FORBIDDEN: UserActivationForbiddenResponseSerializer,
        },
    )
    def get(self, request: Request, uid: str, token: str) -> Response:
        """Activate a user account.

        This view allows users to activate their accounts using the activation link sent to their email.
        The activation link is valid for 30 minutes and can only be used once.

        Args:
            request (Request): The HTTP request object.
            uid (str): The base64-encoded user ID.
            token (str): The activation token.

        Returns:
            Response: The HTTP response object.
        """

        try:
            try:
                # Get the activation token from the database with a single query that includes user data
                activation_token = get_object_or_404(
                    UserActivationToken.objects.select_related("user"),
                    uid=uid,
                    token=token,
                )

            except Http404:
                # Return 403 Forbidden with an error message
                return Response(
                    {"error": "Invalid or already used activation link"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Check if the token has expired
            if activation_token.is_expired:
                # Delete the expired token and return error response in a single transaction
                activation_token.delete()

                # Return 403 Forbidden with error message
                return Response(
                    {"error": "Activation link has expired"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Get the user associated with the token (already loaded with select_related)
            user = activation_token.user

            # Prepare flag for atomic update
            user.is_active = True

            # Use transaction.atomic to ensure both operations complete together
            with transaction.atomic():
                # Save the user
                user.save(update_fields=["is_active"])

                # Delete the token since it's been used
                activation_token.delete()

            # Get domain part for the email footer from settings
            domain_part = settings.ACTIVATION_DOMAIN

            # Prepare activation success email context
            context = {
                "user": user,
                "current_year": timezone.now().year,
                "domain_part": domain_part,
            }

            # Send activation success email using utility function
            send_templated_mail(
                template_name="users/user_activation_success.html",
                subject="Account Activated Successfully",
                context=context,
                recipient_list=[user.email],
            )

            # Return success response
            return Response(
                {"message": "Account activated successfully"},
                status=status.HTTP_200_OK,
            )

        except (TypeError, ValueError, AttributeError):
            # Return error response for specific exceptions
            return Response(
                {"error": "Invalid activation link"},
                status=status.HTTP_403_FORBIDDEN,
            )


# User login view (extends TokenObtainPairView)
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
    def handle_exception(self, exc):
        """Handle exceptions for the login view.

        This method handles exceptions for the login view.

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

        Raises:
            AuthenticationFailed: If authentication fails.
        """

        try:
            # Validate the serializer
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Return the tokens
            return Response(serializer.validated_data)

        except (TokenError, AuthenticationFailed, serializers.ValidationError) as e:
            # Custom error response with only the error field
            return Response(
                {"error": str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )


# User relogin view (extends TokenRefreshView)
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
        return Response({"access": serializer.validated_data["access"]})


# User me view
class UserMeView(APIView):
    """User me view.

    This view handles the authenticated user's profile information.
    GET: Returns the user's profile information.
    PATCH: Updates the user's profile information (username, first name, last name).
    It requires a valid JWT access token for authentication.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        authentication_classes (list): The authentication classes for the view.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Define the permission classes
    permission_classes = [IsAuthenticated]

    # Define the authentication classes
    authentication_classes = [JWTAuthentication]

    # Define the object label
    object_label = "user"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the user me view.

        This method handles exceptions for the user me view.

        Args:
            exc: The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return custom format for authentication errors
        return Response(
            {"status_code": status.HTTP_401_UNAUTHORIZED, "error": str(exc)},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Define the schema for GET method
    @extend_schema(
        tags=["Users"],
        summary="Get authenticated user profile.",
        description="""
        Returns the authenticated user's profile information.
        Requires a valid JWT access token for authentication.
        """,
        responses={
            status.HTTP_200_OK: UserProfileResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: UserProfileErrorResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        """Handle GET request for user profile.

        This method returns the authenticated user's profile information.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Serialize the authenticated user
        serializer = UserProfileSerializer(request.user)

        # Return the serialized user data
        return Response(serializer.data)

    # Define the schema for PATCH method
    @extend_schema(
        tags=["Users"],
        summary="Update authenticated user profile.",
        description="""
        Updates the authenticated user's profile information.
        Users can update their username, first name, and last name.
        Requires a valid JWT access token for authentication.
        """,
        request=UserProfileUpdateSerializer,
        responses={
            status.HTTP_200_OK: UserProfileUpdateResponseSerializer,
            status.HTTP_400_BAD_REQUEST: UserProfileUpdateErrorResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: UserProfileErrorResponseSerializer,
        },
    )
    def patch(self, request: Request) -> Response:
        """Handle PATCH request for updating user profile.

        This method updates the authenticated user's profile information.
        Users can update their username, first name, and last name.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """
        # Create serializer instance with request data and context
        serializer = UserProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        # Validate the serializer
        if serializer.is_valid():
            # Save the updated user
            serializer.save()

            # Return the updated user profile
            return Response(UserProfileSerializer(request.user).data)

        # Return validation errors
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# User deactivate view
class UserDeactivateView(APIView):
    """User deactivate view.

    This view handles deactivating the authenticated user's account.
    POST: Deactivates the user's account after password verification.
    It requires a valid JWT access token for authentication.

    Attributes:
        renderer_classes (list): The renderer classes for the view.
        permission_classes (list): The permission classes for the view.
        authentication_classes (list): The authentication classes for the view.
        object_label (str): The object label for the response.
    """

    # Define the renderer classes
    renderer_classes = [GenericJSONRenderer]

    # Define the permission classes
    permission_classes = [IsAuthenticated]

    # Define the authentication classes
    authentication_classes = [JWTAuthentication]

    # Define the object label
    object_label = "user"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc):
        """Handle exceptions for the user me view.

        This method handles exceptions for the user me view.

        Args:
            exc: The exception that occurred.

        Returns:
            Response: The HTTP response object.
        """

        # Return custom format for authentication errors
        return Response(
            {
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": str(exc.detail.get("detail")),
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Define the schema for POST method
    @extend_schema(
        tags=["Users"],
        summary="Deactivate authenticated user account.",
        description="""
        Deactivates the authenticated user's account.
        Requires the current password to be entered twice for verification.
        This action cannot be undone through the API.
        """,
        request=UserDeactivateSerializer,
        responses={
            status.HTTP_200_OK: UserDeactivateSuccessResponseSerializer,
            status.HTTP_400_BAD_REQUEST: UserDeactivateErrorResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: UserProfileErrorResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        """Handle POST request for deactivating user account.

        This method deactivates the authenticated user's account after verifying their password.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """

        # Get the user
        user = request.user

        # Check if the user is already inactive
        if not user.is_active:
            return Response(
                {"error": "This account is already inactive."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create serializer instance with request data and context
        serializer = UserDeactivateSerializer(
            data=request.data,
            context={"request": request},
        )

        # Validate the serializer
        if serializer.is_valid():
            # Deactivate the user account
            user.is_active = False
            user.save(update_fields=["is_active"])

            # Send account deactivation email
            context = {
                "user": user,
                "current_year": timezone.now().year,
                "domain_part": settings.ACTIVATION_DOMAIN,
            }

            # Send deactivation email
            send_templated_mail(
                template_name="users/user_deactivation.html",
                subject="Account Deactivated",
                context=context,
                recipient_list=[user.email],
            )

            # Return success response
            return Response({"message": "Account deactivated successfully."})

        # Return validation errors
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
