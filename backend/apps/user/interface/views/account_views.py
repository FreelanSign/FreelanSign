# apps/user/interface/views/account_views.py
"""
REST API ViewSet for Account resource.

ARCHITECTURE DECISIONS:
1. Uses ModelViewSet (not ViewSet) - DRF idiomatic for CRUD
2. get_queryset() returns all accounts - permissions handle 403 (not queryset filtering)
3. Serializers read Django models directly - no manual dict mapping
4. partial=True for PATCH - DRF handles merging, no manual logic

@author: @Bertrand2808
@since: 2025-11-26
@version: 2.0
"""

import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)

from apps.core.models.audit import AuditLog

# AIDEV_NOTE: audot logging for sensitive account actions (create/ RGPD delete)
# always use `log_audit` + `AuditLog.Action` instead of touching AuditLog.objects.create(...)
from apps.core.services.audit import log_audit
from apps.user.adapters.persistence.django_account_repository import DjangoAccountRepository
from apps.user.adapters.system_clock import SystemClock
from apps.user.application.dto.account_inputs import CreateAccountInput, UpdateAccountInput
from apps.user.application.errors import AccountNotFoundError as DomainAccountNotFoundError
from apps.user.application.errors import CannotDeleteAccountError
from apps.user.application.usecases.create_account import CreateAccount
from apps.user.application.usecases.deactivate_account import DeactivateAccount
from apps.user.application.usecases.get_user_accounts import GetUserAccounts
from apps.user.application.usecases.rgpd_delete_account import RGPDDeleteAccount
from apps.user.application.usecases.update_account import UpdateAccount
from apps.user.domain.errors import AccountPolicyError, DuplicateAccountNameError
from apps.user.interface.permissions import IsAccountOwner
from apps.user.interface.serializers import AccountInputSerializer, AccountOutputSerializer
from apps.user.models.account import Account


class AccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Account CRUD operations.

    Combines Clean Architecture (use cases) with DRF idioms:
    - Use cases handle business logic
    - DRF handles HTTP/serialization concerns
    - Permissions handle authorization (not queryset filtering)
    """

    queryset = Account.objects.all()
    serializer_class = AccountOutputSerializer
    permission_classes = [IsAuthenticated, IsAccountOwner]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Dependency injection (production adapters)
        self.repository = DjangoAccountRepository()
        self.clock = SystemClock()

    def get_queryset(self):
        """
        Return ALL accounts - permissions handle authorization.

        CRITICAL: Do NOT filter by user here. This would cause 404 instead of 403
        when a user tries to access another user's account.

        The IsAccountOwner permission class will properly return 403 Forbidden.
        """
        return Account.objects.all()

    def list(self, request):
        """
        GET /api/accounts/

        List accounts - admin sees all, regular users see only their own.
        """
        logger.info(f"[ACCOUNT LIST] Start - user={request.user.id}")
        user = request.user

        try:
            # Admin sees all accounts
            if hasattr(user, "profile") and user.profile.role == "admin":
                logger.info(f"[ACCOUNT LIST] Admin mode")
                accounts = Account.objects.all()
            else:
                # Regular users see only their own
                logger.info(f"[ACCOUNT LIST] Regular user mode")
                accounts = Account.objects.filter(user=user)

            logger.info(f"[ACCOUNT LIST] Found {accounts.count()} accounts")
            # DRF serializer reads model attributes directly
            serializer = self.get_serializer(accounts, many=True)
            logger.info(f"[ACCOUNT LIST] Serializer created, returning data")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"[ACCOUNT LIST] Error: {type(e).__name__}: {e}", exc_info=True)
            raise

    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/accounts/{id}/

        DRF automatically calls:
        1. get_object() → fetch from DB
        2. check_object_permissions() → IsAccountOwner validates
        3. Serializer reads model attributes directly
        """
        logger.info(f"[ACCOUNT RETRIEVE] Start - user={request.user.id}, kwargs={kwargs}")
        try:
            instance = self.get_object()  # DRF handles 404 + permission 403
            logger.info(f"[ACCOUNT RETRIEVE] Got instance id={instance.id}")
            serializer = self.get_serializer(instance)
            logger.info(f"[ACCOUNT RETRIEVE] Serializer created, returning data")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"[ACCOUNT RETRIEVE] Error: {type(e).__name__}: {e}", exc_info=True)
            raise

    def create(self, request):
        """
        POST /api/accounts/

        Create account via use case.
        """
        logger.info(f"[CREATE ACCOUNT] Received request.data: {request.data}")
        logger.info(f"[CREATE ACCOUNT] User ID: {request.user.id}")

        # Validate input
        input_serializer = AccountInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        logger.info(f"[CREATE ACCOUNT] Validated data: {input_serializer.validated_data}")

        # Create DTO for use case
        input_dto = CreateAccountInput(user_id=request.user.id, **input_serializer.validated_data)
        logger.info(
            f"[CREATE ACCOUNT] Created DTO: user_id={input_dto.user_id}, display_name={input_dto.display_name}, legal_form={input_dto.legal_form}, legal_id={input_dto.legal_id}"
        )

        try:
            # Execute use case
            use_case = CreateAccount(repository=self.repository, clock=self.clock)
            logger.info(f"[CREATE ACCOUNT] Executing use case...")
            account_vm = use_case.execute(input_dto)
            logger.info(f"[CREATE ACCOUNT] Use case executed successfully, account_id={account_vm.id}")

            # AIDEV_NOTE: audit log must only be emitted if use case succeeds
            log_audit(
                action=AuditLog.Action.ACCOUNT_CREATED,
                actor=request.user,
                target_model="Account",
                target_id=account_vm.id,
                request=request,
                metadata={
                    # keep minimal: no encrypted data here
                    "display_name": getattr(account_vm, "display_name", None),
                },
            )

            # Serialize ViewModel (DRF reads attributes directly)
            serializer = self.get_serializer(account_vm)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except AccountPolicyError as e:
            logger.error(f"[CREATE ACCOUNT] AccountPolicyError: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"[CREATE ACCOUNT] Unexpected error: {type(e).__name__}: {e}", exc_info=True)
            raise

    def update(self, request, *args, **kwargs):
        """
        PUT /api/accounts/{id}/

        Update account via use case.
        """
        instance = self.get_object()  # DRF handles 404 + 403

        # Validate input
        input_serializer = AccountInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        # Create DTO for use case
        input_dto = UpdateAccountInput(account_id=instance.id, **input_serializer.validated_data)

        try:
            # Execute use case
            use_case = UpdateAccount(repository=self.repository, clock=self.clock)
            account_vm = use_case.execute(input_dto)

            # Serialize output
            serializer = self.get_serializer(account_vm)
            return Response(serializer.data)

        except DomainAccountNotFoundError:
            return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
        except AccountPolicyError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /api/accounts/{id}/

        DRF idiom: Use serializer with partial=True (no manual merging).
        """
        instance = self.get_object()  # DRF handles 404 + 403

        # DRF automatically merges with partial=True
        input_serializer = AccountInputSerializer(
            data=request.data, partial=True  # ← DRF magic: only validates provided fields
        )
        input_serializer.is_valid(raise_exception=True)

        # Merge with existing data for use case
        existing_data = {
            "display_name": instance.display_name,
            "legal_form": instance.legal_form,
            "legal_id": instance.legal_id,
            "domain_id": instance.domain_id,
            "default_rate_cents": instance.default_rate_cents,
            "service_type_ids": list(instance.service_types.values_list("id", flat=True)),
        }
        merged_data = {**existing_data, **input_serializer.validated_data}

        # Create DTO for use case
        input_dto = UpdateAccountInput(account_id=instance.id, **merged_data)

        try:
            # Execute use case
            use_case = UpdateAccount(repository=self.repository, clock=self.clock)
            account_vm = use_case.execute(input_dto)

            # Serialize output
            serializer = self.get_serializer(account_vm)
            return Response(serializer.data)

        except DomainAccountNotFoundError:
            return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
        except AccountPolicyError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/accounts/{id}/

        RGPD soft delete with cascade to Clients.
        Blocks if active Quotes exist (DRAFT, SENT, ACCEPTED).
        """
        instance = self.get_object()  # DRF handles 404 + 403
        audit_metadata = {
            "display_name": instance.display_name,
            "user_id": instance.user_id,
        }

        try:
            # Execute RGPD delete use case (soft delete with cascade)
            use_case = RGPDDeleteAccount()
            use_case.execute(account_id=instance.id)

            # AIDEV_NOTE: audit log must only be emitted if use case succeeds
            # DO NOT move this call before use_case.execute()
            log_audit(
                action=AuditLog.Action.ACCOUNT_ANONYMIZED,
                actor=request.user,
                target_model="Account",
                target_id=instance.id,
                request=request,
                metadata=audit_metadata,
            )

            return Response(status=status.HTTP_204_NO_CONTENT)

        except DomainAccountNotFoundError:
            return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
        except CannotDeleteAccountError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["post"],
        url_path="logo",
        permission_classes=[IsAuthenticated, IsAccountOwner],
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_logo(self, request, pk=None):
        """
        Upload logo image to Supabase Storage.

        Expects multipart/form-data with 'file' field.
        Max size: 2MB. Accepted types: jpeg, png, webp, gif.
        """
        from apps.user.adapters.storage.supabase_storage import (
            SupabaseStorageError,
            get_storage_adapter,
        )

        instance = self.get_object()  # Handles 404 + 403

        logger.info("upload_logo called", extra={"account_id": instance.id, "user_id": request.user.id})

        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        content_type = file.content_type
        filename = file.name

        try:
            storage = get_storage_adapter()
            public_url = storage.upload_logo(
                account_id=instance.id,
                file=file,
                content_type=content_type,
                filename=filename,
            )
        except SupabaseStorageError as e:
            logger.warning(
                "upload_logo failed for account_id=%s: %s",
                instance.id,
                str(e),
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update account with new logo URL
        instance.logo_url = public_url
        instance.save(update_fields=["logo_url", "updated_at"])

        logger.info(
            "upload_logo succeeded for account_id=%s: %s",
            instance.id,
            public_url,
        )
        return Response({"logo_url": public_url}, status=status.HTTP_200_OK)
