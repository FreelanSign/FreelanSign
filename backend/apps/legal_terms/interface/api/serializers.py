"""
DRF serializers for legal terms API endpoints.
"""

from rest_framework import serializers


class ClauseOverrideSerializer(serializers.Serializer):
    """Serializer for clause override data."""

    is_active = serializers.BooleanField(required=False, allow_null=True)
    custom_title = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    custom_body = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    custom_order = serializers.IntegerField(required=False, allow_null=True, min_value=1)


class LegalProfileSerializer(serializers.Serializer):
    """Serializer for legal profile."""

    id = serializers.UUIDField(read_only=True)
    account_id = serializers.CharField(read_only=True)
    template_id = serializers.UUIDField(read_only=True)
    template_version = serializers.CharField(read_only=True)
    clause_overrides = serializers.DictField(
        child=serializers.DictField(),
        read_only=True,
    )


class UpdateClauseInputSerializer(serializers.Serializer):
    """Serializer for updating a single clause."""

    identifier = serializers.CharField(required=True)
    is_active = serializers.BooleanField(required=False, allow_null=True)
    custom_title = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    custom_body = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    custom_order = serializers.IntegerField(required=False, allow_null=True, min_value=1)


class UpdateLegalProfileInputSerializer(serializers.Serializer):
    """Serializer for updating legal profile (list of clause updates)."""

    updates = UpdateClauseInputSerializer(many=True, required=True)


class ClausePreviewSerializer(serializers.Serializer):
    """Serializer for clause preview data."""

    identifier = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    body = serializers.CharField(read_only=True)
    order = serializers.IntegerField(read_only=True)
    is_mandatory = serializers.BooleanField(read_only=True)
    was_customized = serializers.BooleanField(read_only=True)


class PreviewLegalTermsOutputSerializer(serializers.Serializer):
    """Serializer for preview legal terms output."""

    clauses = ClausePreviewSerializer(many=True, read_only=True)
    rendered_html = serializers.CharField(read_only=True)
    rendered_text = serializers.CharField(read_only=True)
    template_version = serializers.CharField(read_only=True)
