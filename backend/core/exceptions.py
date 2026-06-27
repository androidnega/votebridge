"""
VoteBridge custom exceptions.

Domain-specific exceptions are defined here and mapped to HTTP responses
via the custom DRF exception handler in core.handlers.
"""

from rest_framework import status


class VoteBridgeError(Exception):
    """Base exception for all VoteBridge domain errors."""

    default_message = "An unexpected error occurred."
    default_code = "error"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message=None, code=None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        super().__init__(self.message)


class ValidationError(VoteBridgeError):
    default_message = "Validation failed."
    default_code = "validation_error"
    status_code = status.HTTP_400_BAD_REQUEST


class AuthenticationError(VoteBridgeError):
    default_message = "Authentication failed."
    default_code = "authentication_error"
    status_code = status.HTTP_401_UNAUTHORIZED


class PermissionDeniedError(VoteBridgeError):
    default_message = "You do not have permission to perform this action."
    default_code = "permission_denied"
    status_code = status.HTTP_403_FORBIDDEN


class NotFoundError(VoteBridgeError):
    default_message = "The requested resource was not found."
    default_code = "not_found"
    status_code = status.HTTP_404_NOT_FOUND


class ConflictError(VoteBridgeError):
    default_message = "The request conflicts with the current state."
    default_code = "conflict"
    status_code = status.HTTP_409_CONFLICT


class ServiceUnavailableError(VoteBridgeError):
    default_message = "The service is temporarily unavailable."
    default_code = "service_unavailable"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
