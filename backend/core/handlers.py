"""
Custom DRF exception handler for VoteBridge.
"""

import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

from core.exceptions import VoteBridgeError

logger = logging.getLogger("votebridge")


def custom_exception_handler(exc, context):
    """
    Return a consistent JSON error envelope for all API exceptions.

    Response format:
        {
            "success": false,
            "error": {
                "code": "...",
                "message": "...",
                "details": {...}  # optional
            }
        }
    """
    if isinstance(exc, VoteBridgeError):
        logger.warning(
            "VoteBridge error [%s]: %s",
            exc.code,
            exc.message,
            extra={"view": context.get("view")},
        )
        return Response(
            {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                },
            },
            status=exc.status_code,
        )

    response = exception_handler(exc, context)

    if response is not None:
        error_code = _resolve_error_code(exc)
        error_message = _resolve_error_message(exc, response)
        error_details = _resolve_error_details(response)

        payload = {
            "success": False,
            "error": {
                "code": error_code,
                "message": error_message,
            },
        }
        if error_details:
            payload["error"]["details"] = error_details

        response.data = payload

        if response.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
            logger.error(
                "Unhandled API exception: %s",
                exc,
                exc_info=exc,
                extra={"view": context.get("view")},
            )
        else:
            logger.warning(
                "API exception [%s]: %s",
                error_code,
                error_message,
                extra={"view": context.get("view")},
            )

        return response

    if isinstance(exc, (Http404, PermissionDenied)):
        status_code = (
            status.HTTP_404_NOT_FOUND
            if isinstance(exc, Http404)
            else status.HTTP_403_FORBIDDEN
        )
        code = "not_found" if isinstance(exc, Http404) else "permission_denied"
        message = str(exc) or (
            "Not found." if isinstance(exc, Http404) else "Permission denied."
        )
        return Response(
            {
                "success": False,
                "error": {"code": code, "message": message},
            },
            status=status_code,
        )

    logger.error(
        "Unhandled exception: %s",
        exc,
        exc_info=exc,
        extra={"view": context.get("view")},
    )
    return Response(
        {
            "success": False,
            "error": {
                "code": "internal_error",
                "message": "An internal server error occurred.",
            },
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _resolve_error_code(exc):
    if hasattr(exc, "default_code"):
        return exc.default_code
    return exc.__class__.__name__.lower()


def _resolve_error_message(exc, response):
    if hasattr(exc, "detail"):
        detail = exc.detail
        if isinstance(detail, list) and detail:
            return str(detail[0])
        if isinstance(detail, dict):
            first_key = next(iter(detail))
            first_value = detail[first_key]
            if isinstance(first_value, list) and first_value:
                return str(first_value[0])
            return str(first_value)
        return str(detail)
    return str(exc)


def _resolve_error_details(response):
    if not isinstance(response.data, dict):
        return None
    if "detail" in response.data and len(response.data) == 1:
        return None
    return response.data
