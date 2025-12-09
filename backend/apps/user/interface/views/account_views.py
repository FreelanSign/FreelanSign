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
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)

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
        user = request.user

        # Admin sees all accounts
        if hasattr(user, "profile") and user.profile.role == "admin":
            accounts = Account.objects.all()
        else:
            # Regular users see only their own
            accounts = Account.objects.filter(user=user)

        # DRF serializer reads model attributes directly
        serializer = self.get_serializer(accounts, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/accounts/{id}/

        DRF automatically calls:
        1. get_object() → fetch from DB
        2. check_object_permissions() → IsAccountOwner validates
        3. Serializer reads model attributes directly
        """
        instance = self.get_object()  # DRF handles 404 + permission 403
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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

        try:
            # Execute RGPD delete use case (soft delete with cascade)
            use_case = RGPDDeleteAccount()
            use_case.execute(account_id=instance.id)

            return Response(status=status.HTTP_204_NO_CONTENT)

        except DomainAccountNotFoundError:
            return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
        except CannotDeleteAccountError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
