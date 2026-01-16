# apps/user/interface/serializers/account_serializers.py
"""
Serializers for Account REST API.

@author: @Bertrand2808
@since: 2025-11-26
@version: 1.0
"""
import logging

from rest_framework import serializers

from apps.user.domain.errors import AccountPolicyError
from apps.user.domain.policies.account_policy import AccountPolicy

logger = logging.getLogger(__name__)


class AccountInputSerializer(serializers.Serializer):
    """
    Input serializer for creating/updating accounts.

    Validates input using AccountPolicy from domain layer.
    """

    display_name = serializers.CharField(max_length=255)
    legal_form = serializers.ChoiceField(choices=["micro", "eirl", "eurl", "sasu", "other"], required=False, allow_null=True)
    legal_id = serializers.CharField(max_length=14, required=False, allow_null=True, allow_blank=True)
    domain_id = serializers.IntegerField(required=False, allow_null=True)
    default_rate_cents = serializers.IntegerField(required=False, allow_null=True)
    professional_headline = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    service_type_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )

    def validate(self, data):
        """
        Validate using domain policy.

        For partial updates (PATCH), only validate provided fields.
        The view layer will merge with existing data before calling the use case.

        Raises:
            ValidationError: If data doesn't meet domain rules
        """
        logger.info(f"[SERIALIZER] validate() called with data: {data}")
        logger.info(
            f"[SERIALIZER] Checking fields: display_name={data.get('display_name')}, legal_form={data.get('legal_form')}"
        )

        # Only validate if all required fields are present
        # For PATCH requests, the view merges with existing data
        if "display_name" in data:
            logger.info(f"[SERIALIZER] Running AccountPolicy validation...")
            try:
                # Use AccountPolicy for domain validation
                AccountPolicy.validate_account_data(
                    display_name=data["display_name"],
                    legal_form=data.get("legal_form"),
                    legal_id=data.get("legal_id"),
                    domain_id=data.get("domain_id"),
                )
                logger.info(f"[SERIALIZER] AccountPolicy validation passed")
            except AccountPolicyError as e:
                logger.error(f"[SERIALIZER] Domain validation failed: {e}")
                raise serializers.ValidationError(str(e))
        return data


class AccountOutputSerializer(serializers.Serializer):
    """
    Output serializer for Account (read operations).

    Returns account data without nested objects (IDs only).
    Handles both AccountViewModel and Django Account model.
    """

    id = serializers.IntegerField()
    display_name = serializers.CharField()
    legal_form = serializers.CharField(allow_null=True)
    legal_id = serializers.CharField(allow_null=True)
    domain_id = serializers.SerializerMethodField()
    default_rate_cents = serializers.IntegerField(allow_null=True)
    professional_headline = serializers.CharField(allow_null=True)
    service_type_ids = serializers.SerializerMethodField()
    is_active = serializers.BooleanField()
    logo_url = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def get_domain_id(self, obj):
        """
        Extract domain_id from either ViewModel or Django model.

        Args:
            obj: AccountViewModel or Account Django model

        Returns:
            Domain ID or None
        """
        # If it's an AccountViewModel (has domain_id attribute)
        if hasattr(obj, "domain_id"):
            return obj.domain_id
        # If it's a Django model (has domain ForeignKey)
        elif hasattr(obj, "domain_id"):
            return obj.domain_id
        elif hasattr(obj, "domain"):
            return obj.domain.id if obj.domain else None
        return None

    def get_service_type_ids(self, obj):
        """
        Extract service_type_ids from either ViewModel or Django model.

        Args:
            obj: AccountViewModel or Account Django model

        Returns:
            List of service type IDs
        """
        # If it's an AccountViewModel (has service_type_ids attribute)
        if hasattr(obj, "service_type_ids"):
            return obj.service_type_ids
        # If it's a Django model (has service_types ManyToMany relation)
        elif hasattr(obj, "service_types"):
            return list(obj.service_types.values_list("id", flat=True))
        return []
