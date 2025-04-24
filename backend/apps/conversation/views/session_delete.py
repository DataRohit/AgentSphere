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
from apps.conversation.models import Session
from apps.conversation.serializers.session_delete import (
    SessionDeleteAuthErrorResponseSerializer,
    SessionDeleteNotFoundResponseSerializer,
    SessionDeletePermissionDeniedResponseSerializer,
    SessionDeleteSuccessResponseSerializer,
)

# Get the User model
User = get_user_model()


# Session delete view
class SessionDeleteView(APIView):
    """View for deleting a session.

    This view allows authenticated users to delete a session.
    Only the user associated with the chat or the owner of the organization can delete the session.

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
    object_label = "session"

    # Override the handle_exception method to customize error responses
    def handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions for the session deletion view.

        This method handles exceptions for the session deletion view.

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

        # Return the exception as a standard error
        return Response(
            {"error": str(exc)},
            status=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        )

    # Define the schema for the DELETE view
    @extend_schema(
        tags=["Sessions"],
        summary="Delete a session.",
        description="""
        Deletes a session by its ID.
        Only the user associated with the chat or the owner of the organization can delete the session.
        """,
        responses={
            status.HTTP_200_OK: SessionDeleteSuccessResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: SessionDeleteAuthErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: SessionDeletePermissionDeniedResponseSerializer,
            status.HTTP_404_NOT_FOUND: SessionDeleteNotFoundResponseSerializer,
        },
    )
    def delete(self, request: Request, session_id: str) -> Response:
        """Delete a session.

        This method deletes a session by its ID.
        Only the user associated with the chat or the owner of the organization can delete the session.

        Args:
            request (Request): The HTTP request object.
            session_id (str): The ID of the session.

        Returns:
            Response: The HTTP response object.
        """

        # Get the authenticated user
        user = request.user

        try:
            # Try to get the session
            session = Session.objects.get(id=session_id)

            # Check if the user has permission to delete this session
            has_permission = False

            # If the session has a single chat
            if session.single_chat:
                # Check if the user is the owner of the single chat or the owner of the organization
                if session.single_chat.user == user or (
                    session.single_chat.organization and user == session.single_chat.organization.owner
                ):
                    has_permission = True

            # If the session has a group chat
            elif session.group_chat:
                # Check if the user is the owner of the organization that the chat belongs to
                if session.group_chat.organization and user == session.group_chat.organization.owner:
                    has_permission = True

            # If the user doesn't have permission
            if not has_permission:
                # Return a permission denied error
                return Response(
                    {"error": "You do not have permission to delete this session."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Delete the session
            session.delete()

            # Return a successful response
            return Response(
                {"session": {"message": "Session deleted successfully."}},
                status=status.HTTP_200_OK,
            )

        except Session.DoesNotExist:
            # Return a not found error
            return Response(
                {"error": "Session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
