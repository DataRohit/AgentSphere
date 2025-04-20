# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

# Local application imports
from apps.chats.models import GroupChat, SingleChat
from apps.common.serializers import GenericResponseSerializer
from apps.conversation.models import Session
from apps.conversation.serializers.session import SessionResponseSchema


# Session create serializer
class SessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new session.

    This serializer is used for validating and creating a new session.
    It validates the chat_id and llm_id from the request body and determines
    whether it's a single chat or group chat.

    Attributes:
        chat_id (UUIDField): The ID of the chat to create a session for (required).
        llm_id (UUIDField): The ID of the LLM to use for this session (required).
    """

    # Chat ID field
    chat_id = serializers.UUIDField(
        required=True,
        help_text=_("ID of the chat to create a session for."),
    )

    # LLM ID field
    llm_id = serializers.UUIDField(
        required=True,
        help_text=_("ID of the LLM to use for this session."),
    )

    # Meta class for SessionCreateSerializer configuration
    class Meta:
        """Meta class for SessionCreateSerializer configuration.

        Attributes:
            model (Session): The model class.
            fields (list): The fields to include in the serializer.
        """

        # Model to use for the serializer
        model = Session

        # Fields to include in the serializer
        fields = [
            "chat_id",
            "llm_id",
        ]

    # Validate method to check if the chat exists and the user has permission
    def validate(self, attrs: dict) -> dict:
        """Validate the chat ID, LLM ID, and check permissions.

        This method validates that:
        1. The chat exists and the user has permission to access it.
        2. The LLM exists and the user has permission to use it.
        3. There's no active session for the chat.

        Args:
            attrs (dict): The attributes to validate.

        Returns:
            dict: The validated attributes.

        Raises:
            serializers.ValidationError: If validation fails.
        """

        # Get the chat ID from the attributes
        chat_id = attrs.get("chat_id")

        # Get the request from the context
        request = self.context.get("request")

        # Get the authenticated user
        user = request.user

        # Get the LLM ID from the attributes
        llm_id = attrs.get("llm_id")

        # Import LLM model here to avoid circular imports
        from apps.llms.models import LLM

        # Validate LLM ID
        try:
            # Try to get the LLM
            llm = LLM.objects.get(id=llm_id)

            # Check if the user has permission to use this LLM
            if llm.user != user and (not llm.organization or user not in llm.organization.members.all()):
                # Raise a validation error
                raise serializers.ValidationError(
                    {
                        "llm_id": [
                            _("You do not have permission to use this LLM."),
                        ],
                    },
                )

            # Store the LLM in attrs for later use
            attrs["llm"] = llm

        except LLM.DoesNotExist:
            # Raise a validation error
            raise serializers.ValidationError(
                {
                    "llm_id": [
                        _("LLM not found."),
                    ],
                },
            ) from None

        # Initialize single chat
        single_chat = None
        try:
            # Get the single chat
            single_chat = SingleChat.objects.get(id=chat_id)

            # Check if the user has permission to access the single chat
            if single_chat.user != user and not (
                single_chat.is_public and single_chat.organization.members.filter(id=user.id).exists()
            ):
                # Raise a validation error if the user does not have permission to access the single chat
                raise serializers.ValidationError({"chat_id": [_("You do not have permission to access this chat.")]})

            # Check if there's already an active session for this chat
            if Session.objects.filter(single_chat=single_chat, is_active=True).exists():
                # Raise a validation error if there's already an active session for this chat
                raise serializers.ValidationError({"chat_id": [_("There is already an active session for this chat.")]})

            # Store the single chat in the validated data
            attrs["single_chat"] = single_chat
            attrs["group_chat"] = None

            # Return the validated data
            return attrs  # noqa: TRY300

        # If the single chat does not exist
        except SingleChat.DoesNotExist:
            # Continue to try group chat
            pass

        # Initialize group chat
        group_chat = None
        try:
            # Get the group chat
            group_chat = GroupChat.objects.get(id=chat_id)

            # Check if the user has permission to access the group chat
            if group_chat.user != user and not (
                group_chat.is_public and group_chat.organization.members.filter(id=user.id).exists()
            ):
                # Raise a validation error if the user does not have permission to access the group chat
                raise serializers.ValidationError({"chat_id": [_("You do not have permission to access this chat.")]})

            # Check if there's already an active session for this chat
            if Session.objects.filter(group_chat=group_chat, is_active=True).exists():
                # Raise a validation error if there's already an active session for this chat
                raise serializers.ValidationError({"chat_id": [_("There is already an active session for this chat.")]})

            # Store the group chat in the validated data
            attrs["group_chat"] = group_chat
            attrs["single_chat"] = None

            # Return the validated data
            return attrs  # noqa: TRY300

        # If the group chat does not exist
        except GroupChat.DoesNotExist:
            # Set the error message
            error_message = _("Chat not found.")

            # Raise a validation error if the group chat does not exist
            raise serializers.ValidationError({"chat_id": [error_message]}) from None

    # Create method to create a new session
    def create(self, validated_data: dict) -> Session:
        """Create a new session with the validated data.

        Args:
            validated_data (dict): The validated data.

        Returns:
            Session: The newly created session.
        """

        # Extract the chat data
        single_chat = validated_data.get("single_chat")
        group_chat = validated_data.get("group_chat")

        # Extract the LLM
        llm = validated_data.get("llm")

        # Generate the selector prompt for group chat
        selector_prompt = ""
        if validated_data.get("group_chat"):
            # Start with the base prompt
            selector_prompt = "Select an agent to perform task.\n\n"

            # Traverse through the agents
            for agent in validated_data["group_chat"].agents.all():
                # Add the agent to the selector prompt
                selector_prompt += f"{agent.name} - {agent.description}\n"

        # Remove llm_id and chat_id from validated_data as they're not fields in the Session model
        validated_data.pop("llm_id", None)
        validated_data.pop("chat_id", None)

        # Create and return a new session
        return Session.objects.create(
            single_chat=single_chat,
            group_chat=group_chat,
            llm=llm,
            selector_prompt=selector_prompt,
            is_active=True,
        )


# Session create success response serializer
class SessionCreateSuccessResponseSerializer(GenericResponseSerializer):
    """Serializer for successful session creation response.

    This serializer defines the structure of the session creation success response.
    It includes a status code and a session object with WebSocket URL.

    Attributes:
        status_code (int): The status code of the response.
        session (SessionResponseSchema): The session details with WebSocket URL.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_201_CREATED,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Session data
    session = SessionResponseSchema(
        help_text=_("The session details with WebSocket URL."),
        read_only=True,
    )


# Session create error response serializer
class SessionCreateErrorResponseSerializer(GenericResponseSerializer):
    """Serializer for session creation error response.

    This serializer defines the structure of the session creation error response.
    It includes a status code and error details.

    Attributes:
        status_code (int): The status code of the response.
        error (SessionCreateErrorsSerializer): The error details.
    """

    # Nested serializer defining the structure of the actual errors
    class SessionCreateErrorsSerializer(serializers.Serializer):
        """Session Creation Errors serializer.

        Attributes:
            chat_id (list): Errors related to the chat ID field.
            llm_id (list): Errors related to the LLM ID field.
            non_field_errors (list): Non-field specific errors.
        """

        # Chat ID field
        chat_id = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the chat ID field."),
        )

        # LLM ID field
        llm_id = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Errors related to the LLM ID field."),
        )

        # Non-field errors
        non_field_errors = serializers.ListField(
            child=serializers.CharField(),
            required=False,
            help_text=_("Non-field specific errors."),
        )

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_400_BAD_REQUEST,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error details
    error = SessionCreateErrorsSerializer(
        help_text=_("Detailed error information."),
        read_only=True,
    )


# Session auth error response serializer
class SessionAuthErrorResponseSerializer(GenericResponseSerializer):
    """Serializer for session authentication error response.

    This serializer defines the structure of the authentication error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response.
        error (str): The error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_401_UNAUTHORIZED,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("Authentication credentials were not provided."),
        read_only=True,
        help_text=_("Error message."),
    )


# Session not found error response serializer
class SessionNotFoundErrorResponseSerializer(GenericResponseSerializer):
    """Serializer for session not found error response.

    This serializer defines the structure of the not found error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response.
        error (str): The error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_404_NOT_FOUND,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("Chat not found."),
        read_only=True,
        help_text=_("Error message."),
    )


# Session permission denied response serializer
class SessionPermissionDeniedResponseSerializer(GenericResponseSerializer):
    """Serializer for session permission denied response.

    This serializer defines the structure of the permission denied error response.
    It includes a status code and an error message.

    Attributes:
        status_code (int): The status code of the response.
        error (str): The error message.
    """

    # Status code
    status_code = serializers.IntegerField(
        default=status.HTTP_403_FORBIDDEN,
        read_only=True,
        help_text=_("HTTP status code for the response."),
    )

    # Error message
    error = serializers.CharField(
        default=_("You do not have permission to access this chat."),
        read_only=True,
        help_text=_("Error message."),
    )
