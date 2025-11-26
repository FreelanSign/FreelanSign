# apps/user/interface/middleware/account_context.py
"""
Middleware to load Account context from X-Account-Id header.

Behavior:
- If X-Account-Id present: Load & validate account ownership
- If absent: Fallback to user.accounts.first() (active only)
- Store in request.account (can be None)

@author: @Bertrand2808
@since: 2025-11-26
@version: 1.0
"""
from apps.user.interface.exceptions import AccountNotFoundError
from apps.user.models.account import Account


class AccountContextMiddleware:
    """
    Middleware to populate request.account from X-Account-Id header.

    Provides smart fallback for backward compatibility:
    - Header present → validates ownership
    - Header absent → uses first active account
    - Not authenticated → request.account = None
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip if not authenticated
        if not request.user.is_authenticated:
            request.account = None
            return self.get_response(request)

        # Get account ID from header
        account_id_header = request.headers.get("X-Account-Id")

        if account_id_header:
            # Header present - validate ownership
            try:
                account_id = int(account_id_header)
                account = Account.objects.get(id=account_id, user=request.user, is_active=True)
                request.account = account
            except (ValueError, Account.DoesNotExist):
                raise AccountNotFoundError(account_id_header)
        else:
            # Fallback to first active account (backward compat)
            request.account = Account.objects.filter(user=request.user, is_active=True).first()

        return self.get_response(request)
