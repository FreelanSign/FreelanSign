# apps/user/interface/exceptions/account_exceptions.py
"""
Custom exceptions for Account interface layer.

@author: @Bertrand2808
@since: 2025-11-25
@version: 1.0
"""

from rest_framework import status
from rest_framework.exceptions import APIException


class AccountContextRequiredError(APIException):
    """
    Raised when X-Account-Id header is required but missing.

    HTTP 428 Precondition Required.
    """

    status_code = status.HTTP_428_PRECONDITION_REQUIRED
    default_code = "account_context_required"
    default_detail = "X-Account-Id header is required for this operation"


class AccountNotFoundError(APIException):
    """
    Raised when account ID doesn't exist or not owned by user.

    HTTP 404 Not Found.
    """

    status_code = status.HTTP_404_NOT_FOUND
    default_code = "account_not_found"
    default_detail = "Account not found or you do not have access"

    def __init__(self, account_id: int | None = None):
        if account_id:
            detail = f"Account {account_id} not found or you do not have access"
        else:
            detail = self.default_detail
        super().__init__(detail=detail)
