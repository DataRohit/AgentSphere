"""Authentication middleware for WebSockets.

This module contains custom authentication middleware for WebSocket connections.
"""

# Standard library imports
import traceback
from collections.abc import Awaitable, Callable
from typing import Any

# Third-party imports
from channels.db import database_sync_to_async


@database_sync_to_async
def get_user(token_key: str) -> tuple[Any, bool]:
    """Get user from JWT token.

    This function validates a JWT token and returns the associated user.

    Args:
        token_key (str): The JWT token.

    Returns:
        tuple[Any, bool]: A tuple containing the user (or None) and a boolean
        indicating whether the token is valid.
    """

    # Import here to avoid circular imports
    from django.contrib.auth.models import AnonymousUser
    from django.db import close_old_connections
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

    # Close old database connections
    close_old_connections()

    # Create JWT authentication instance
    jwt_auth = JWTAuthentication()

    # Initialize user and is_authenticated
    user = None
    is_authenticated = False

    try:
        # Validate the token
        validated_token = jwt_auth.get_validated_token(token_key)

        # Get the user from the validated token
        user = jwt_auth.get_user(validated_token)

        # Set is_authenticated to True if user is not None
        is_authenticated = user is not None

    except (InvalidToken, TokenError):
        # Set user to AnonymousUser
        user = AnonymousUser()

        # Set is_authenticated to False
        is_authenticated = False

    except (ValueError, TypeError, AttributeError):
        # Log the exception
        traceback.print_exc()

        # Set user to AnonymousUser
        user = AnonymousUser()

        # Set is_authenticated to False
        is_authenticated = False

    # Return the user and is_authenticated
    return user, is_authenticated


class JWTAuthMiddleware:
    """JWT authentication middleware for WebSocket connections.

    This middleware authenticates WebSocket connections using JWT tokens.
    It extracts the token from the query string or headers and validates it.

    Attributes:
        inner (ASGIApp): The ASGI application to wrap.
    """

    def __init__(self, inner: Callable) -> None:
        """Initialize the middleware.

        Args:
            inner (Callable): The ASGI application to wrap.
        """

        # Store the ASGI application
        self.inner = inner

    async def __call__(self, scope: dict[str, Any], receive: Callable, send: Callable) -> Awaitable[None]:
        """Process the connection.

        This method extracts the JWT token from the query string or headers,
        validates it, and adds the user to the scope.

        Args:
            scope (dict[str, Any]): The connection scope.
            receive (Callable): The receive function.
            send (Callable): The send function.

        Returns:
            Awaitable[None]: The awaitable result.
        """

        # Import here to avoid circular imports
        from django.db import close_old_connections

        # Close old database connections
        close_old_connections()

        # Initialize token
        token = None

        # Try to get token from query string
        if "query_string" in scope:
            # Decode the query string
            query_string = scope["query_string"].decode("utf-8")

            # Parse the query string
            query_params = dict(param.split("=") for param in query_string.split("&") if "=" in param)

            # Get the token from the query parameters
            token = query_params.get("token")

        # If token is not in query string, try to get it from headers
        if not token and "headers" in scope:
            # Get the headers
            headers = dict(scope["headers"])

            # Get the authorization header
            auth_header = headers.get(b"authorization", b"").decode("utf-8")

            # If the authorization header starts with "Bearer ", extract the token
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]

        # If token is found, authenticate the user
        if token:
            # Get the user from the token
            user, is_authenticated = await get_user(token)

            # Add the user and is_authenticated to the scope
            scope["user"] = user
            scope["is_authenticated"] = is_authenticated

        else:
            # If no token is found, set user to AnonymousUser
            from django.contrib.auth.models import AnonymousUser

            scope["user"] = AnonymousUser()
            scope["is_authenticated"] = False

        # Call the inner application
        return await self.inner(scope, receive, send)


# Function to create a JWT authentication middleware stack
def JWTAuthMiddlewareStack(inner: Callable) -> JWTAuthMiddleware:  # noqa: N802
    """Create a JWT authentication middleware stack.

    This function creates a JWT authentication middleware stack.

    Args:
        inner (Callable): The ASGI application to wrap.

    Returns:
        JWTAuthMiddleware: The JWT authentication middleware.
    """

    # Return the JWT authentication middleware
    return JWTAuthMiddleware(inner)
