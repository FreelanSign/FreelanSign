# apps/user/interface/serializers/account_serializers.py
"""
Serializers for Account REST API.

@author: @Bertrand2808
@since: 2025-11-26
@version: 1.0
"""
from rest_framework import serializers

from apps.user.domain.policies.account_policy import AccountPolicy


class AccountInputSerializer(serializers.Serializer):
    """
    Input serializer for creating/updating accounts.

    Validates input using AccountPolicy from domain layer.
    """

    display_name = serializers.CharField(max_length=255)
    legal_form = serializers.ChoiceField(choices=["micro", "eirl", "eurl", "sasu", "other"], required=False, allow_null=True)
    legal_id = serializers.CharField(max_length=14, required=False, allow_null=True, allow_blank=True)
    domain_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, data):
        """
        Validate using domain policy.

        For partial updates (PATCH), only validate provided fields.
        The view layer will merge with existing data before calling the use case.

        Raises:
            ValidationError: If data doesn't meet domain rules
        """
        # Only validate if all required fields are present
        # For PATCH requests, the view merges with existing data
        if "display_name" in data and "legal_form" in data:
            # Use AccountPolicy for domain validation
            AccountPolicy.validate_account_data(
                display_name=data["display_name"],
                legal_form=data["legal_form"],
                legal_id=data.get("legal_id"),
                domain_id=data.get("domain_id"),
            )
        return data


class AccountOutputSerializer(serializers.Serializer):
    """
    Output serializer for Account (read operations).

    Returns account data without nested objects (IDs only).
    """

    id = serializers.IntegerField()
    display_name = serializers.CharField()
    legal_form = serializers.CharField(allow_null=True)
    legal_id = serializers.CharField(allow_null=True)
    domain_id = serializers.IntegerField(allow_null=True)
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
