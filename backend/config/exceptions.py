# config/exceptions.py
from rest_framework.views import exception_handler as drf_default_handler
from rest_framework.response import Response
from rest_framework import status

def drf_exception_handler(exc, context):
    # Laisse DRF gérer en premier (ValidationError, NotAuthenticated, etc.)
    resp = drf_default_handler(exc, context)
    if resp is not None:
        return resp

    # Fallback générique (loggable)
    return Response(
        {"detail": "Internal server error"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
