from django.db import DatabaseError, IntegrityError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None and isinstance(exc, (DatabaseError, IntegrityError)):
        return Response(
            {
                'error_code': 'database_error',
                'message': 'Database operation failed.',
                'details': [],
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    if response is None and isinstance(exc, Http404):
        return Response(
            {
                'error_code': 'not_found',
                'message': 'Resource was not found.',
                'details': [],
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    if response is None:
        return None

    original = response.data
    error_code = _error_code(exc, response.status_code, original)
    response.data = {
        'error_code': error_code,
        'code': error_code,
        'message': _message(exc, original, error_code),
        'details': _details(exc, original),
    }
    return response


def _error_code(exc, status_code, original):
    if isinstance(original, dict) and 'error_code' in original:
        return original['error_code']
    if isinstance(original, dict) and 'code' in original:
        return original['code']
    if isinstance(exc, ValidationError):
        return 'validation_error'
    if isinstance(exc, APIException):
        return getattr(exc, 'default_code', None) or exc.__class__.__name__.lower()
    if status_code == status.HTTP_404_NOT_FOUND:
        return 'not_found'
    return 'api_error'


def _message(exc, original, error_code):
    if isinstance(original, dict):
        message = original.get('message') or original.get('detail')
        if message:
            return str(message)
    if isinstance(original, list) and original:
        return str(original[0])
    if isinstance(exc, ValidationError):
        return 'Validation failed.'
    return str(getattr(exc, 'detail', 'Request failed.')) or error_code


def _details(exc, original):
    if isinstance(original, dict):
        if 'details' in original:
            return original['details']
        return {
            key: value
            for key, value in original.items()
            if key not in {'code', 'error_code', 'message', 'detail'}
        }
    if isinstance(original, list):
        return original
    detail = getattr(exc, 'detail', None)
    if isinstance(detail, (dict, list)):
        return detail
    return []
