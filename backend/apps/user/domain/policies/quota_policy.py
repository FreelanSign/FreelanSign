# apps/user/domain/policies/quota_policy.py
"""Subscription plan quota validation policy."""

from apps.user.domain.errors import QuotaExceededError


class QuotaPolicy:
    """
    Subscription plan quota validation policy.

    Defines limits for each plan and validates current usage against those limits.

    Plans:
    - beta: Unlimited (for beta testing phase)
    - free: 5 quotes/month, 3 clients
    - pro: Unlimited

    @author: @Bertrand2808
    @since: 2026-01-31
    """

    PLAN_LIMITS = {
        "beta": {"max_quotes_monthly": None, "max_clients": None},
        "free": {"max_quotes_monthly": 5, "max_clients": 3},
        "pro": {"max_quotes_monthly": None, "max_clients": None},
    }

    @staticmethod
    def get_plan_limits(plan: str) -> dict:
        """
        Get quota limits for a given plan.

        Args:
            plan: Plan identifier ('beta', 'free', 'pro')

        Returns:
            dict: Limits dict with 'max_quotes_monthly' and 'max_clients' keys
                  (None = unlimited)

        Note:
            Unknown plans default to 'free' limits for safety.
        """
        return QuotaPolicy.PLAN_LIMITS.get(plan, QuotaPolicy.PLAN_LIMITS["free"])

    @staticmethod
    def validate_quota(
        plan: str,
        current_quotes_this_month: int,
        current_clients: int,
    ) -> None:
        """
        Validate current usage against plan limits.

        Args:
            plan: Account subscription plan
            current_quotes_this_month: Number of quotes created this month
            current_clients: Total number of active clients

        Raises:
            QuotaExceededError: If any limit is exceeded

        Note:
            Beta and Pro plans bypass all checks (unlimited).
            Checks quotes limit before clients limit.
        """
        # Beta plan = unlimited during beta phase
        if plan == "beta":
            return

        limits = QuotaPolicy.get_plan_limits(plan)

        # Check quotes monthly limit
        if limits["max_quotes_monthly"] is not None:
            if current_quotes_this_month >= limits["max_quotes_monthly"]:
                raise QuotaExceededError(
                    f"Monthly quota exceeded ({limits['max_quotes_monthly']} quotes/month for {plan} plan)"
                )

        # Check clients limit
        if limits["max_clients"] is not None:
            if current_clients >= limits["max_clients"]:
                raise QuotaExceededError(f"Client limit reached ({limits['max_clients']} clients for {plan} plan)")
