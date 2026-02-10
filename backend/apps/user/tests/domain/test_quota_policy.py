"""Unit tests for QuotaPolicy."""

import pytest

from apps.user.domain.errors import QuotaExceededError
from apps.user.domain.policies.quota_policy import QuotaPolicy


class TestQuotaPolicyGetPlanLimits:
    """Test get_plan_limits() returns correct limits."""

    def test_beta_plan_limits(self):
        """Beta plan returns unlimited (None) for all quotas."""
        limits = QuotaPolicy.get_plan_limits("beta")

        assert limits == {
            "max_quotes_monthly": None,
            "max_clients": None,
        }

    def test_free_plan_limits(self):
        """Free plan returns 5 quotes/month, 3 clients."""
        limits = QuotaPolicy.get_plan_limits("free")

        assert limits == {
            "max_quotes_monthly": 5,
            "max_clients": 3,
        }

    def test_pro_plan_limits(self):
        """Pro plan returns unlimited (None) for all quotas."""
        limits = QuotaPolicy.get_plan_limits("pro")

        assert limits == {
            "max_quotes_monthly": None,
            "max_clients": None,
        }

    def test_unknown_plan_defaults_to_free(self):
        """Unknown plan defaults to free plan limits."""
        limits = QuotaPolicy.get_plan_limits("unknown")

        assert limits == {
            "max_quotes_monthly": 5,
            "max_clients": 3,
        }


class TestQuotaPolicyValidateQuota:
    """Test validate_quota() enforces limits correctly."""

    def test_beta_plan_allows_unlimited_quotes(self):
        """Beta plan allows unlimited quotes (no exception)."""
        QuotaPolicy.validate_quota(
            plan="beta",
            current_quotes_this_month=1000,
            current_clients=1000,
        )
        # No exception = pass

    def test_beta_plan_allows_unlimited_clients(self):
        """Beta plan allows unlimited clients (no exception)."""
        QuotaPolicy.validate_quota(
            plan="beta",
            current_quotes_this_month=1000,
            current_clients=1000,
        )
        # No exception = pass

    def test_pro_plan_allows_unlimited_quotes(self):
        """Pro plan allows unlimited quotes (no exception)."""
        QuotaPolicy.validate_quota(
            plan="pro",
            current_quotes_this_month=1000,
            current_clients=1000,
        )
        # No exception = pass

    def test_free_plan_allows_within_quote_limit(self):
        """Free plan allows quotes within limit (4/5)."""
        QuotaPolicy.validate_quota(
            plan="free",
            current_quotes_this_month=4,
            current_clients=2,
        )
        # No exception = pass

    def test_free_plan_blocks_at_quote_limit(self):
        """Free plan blocks quote creation at limit (5/5)."""
        with pytest.raises(QuotaExceededError) as exc_info:
            QuotaPolicy.validate_quota(
                plan="free",
                current_quotes_this_month=5,
                current_clients=2,
            )

        assert "Monthly quota exceeded" in str(exc_info.value)
        assert "5 quotes/month" in str(exc_info.value)
        assert "free plan" in str(exc_info.value)

    def test_free_plan_blocks_over_quote_limit(self):
        """Free plan blocks quote creation over limit (6/5)."""
        with pytest.raises(QuotaExceededError):
            QuotaPolicy.validate_quota(
                plan="free",
                current_quotes_this_month=6,
                current_clients=2,
            )

    def test_free_plan_allows_within_client_limit(self):
        """Free plan allows clients within limit (2/3)."""
        QuotaPolicy.validate_quota(
            plan="free",
            current_quotes_this_month=0,
            current_clients=2,
        )
        # No exception = pass

    def test_free_plan_blocks_at_client_limit(self):
        """Free plan blocks client addition at limit (3/3)."""
        with pytest.raises(QuotaExceededError) as exc_info:
            QuotaPolicy.validate_quota(
                plan="free",
                current_quotes_this_month=0,
                current_clients=3,
            )

        assert "Client limit reached" in str(exc_info.value)
        assert "3 clients" in str(exc_info.value)
        assert "free plan" in str(exc_info.value)

    def test_free_plan_blocks_over_client_limit(self):
        """Free plan blocks client addition over limit (4/3)."""
        with pytest.raises(QuotaExceededError):
            QuotaPolicy.validate_quota(
                plan="free",
                current_quotes_this_month=0,
                current_clients=4,
            )

    def test_free_plan_checks_quotes_first(self):
        """Free plan checks quote limit before client limit."""
        with pytest.raises(QuotaExceededError) as exc_info:
            QuotaPolicy.validate_quota(
                plan="free",
                current_quotes_this_month=5,  # At limit
                current_clients=3,  # Also at limit
            )

        # Should raise quote error first
        assert "Monthly quota exceeded" in str(exc_info.value)

    def test_zero_quotes_and_clients_allowed(self):
        """Free plan allows zero usage."""
        QuotaPolicy.validate_quota(
            plan="free",
            current_quotes_this_month=0,
            current_clients=0,
        )
        # No exception = pass
