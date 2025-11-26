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
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.user.adapters.persistence.django_account_repository import DjangoAccountRepository
from apps.user.adapters.system_clock import SystemClock
from apps.user.application.dto.account_inputs import CreateAccountInput, UpdateAccountInput
from apps.user.application.errors import (
    AccountNotFoundError as DomainAccountNotFoundError,
    DuplicateAccountNameError,
)
from apps.user.application.usecases.create_account import CreateAccount
from apps.user.application.usecases.deactivate_account import DeactivateAccount
from apps.user.application.usecases.get_user_accounts import GetUserAccounts
from apps.user.application.usecases.update_account import UpdateAccount
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
        Return queryset for list view.

        NOTE: Returns ALL accounts - IsAccountOwner permission handles 403.
        This maintains semantic distinction between 404 (not exists) and 403 (forbidden).

        Admin users: Can list all accounts
        Regular users: Can only list their own (filtered here for performance)
        """
        user = self.request.user

        # NOTE: Using profile.role instead of Django Groups for now (legacy).
        # TODO v0.3: Migrate to Django Groups + Permissions
        if hasattr(user, "profile") and user.profile.role == "admin":
            return Account.objects.all()
        else:
            # Performance optimization: pre-filter for list view
            # Single retrieve still goes through permission check
            return Account.objects.filter(user=user)

    def list(self, request):
        """
        GET /api/accounts/

        List accounts using Clean Architecture use case.
        """
        use_case = GetUserAccounts(repository=self.repository)

        # Admin can see inactive accounts
        include_inactive = hasattr(request.user, "profile") and request.user.profile.role == "admin"

        result = use_case.execute(user_id=request.user.id, include_inactive=include_inactive)

        # DRF serializer reads ViewModel attributes directly (no manual mapping)
        serializer = self.get_serializer(result.accounts, many=True)
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
        # Validate input
        input_serializer = AccountInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        # Create DTO for use case
        input_dto = CreateAccountInput(user_id=request.user.id, **input_serializer.validated_data)

        try:
            # Execute use case
            use_case = CreateAccount(repository=self.repository, clock=self.clock)
            account_vm = use_case.execute(input_dto)

            # Serialize ViewModel (DRF reads attributes directly)
            serializer = self.get_serializer(account_vm)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except DuplicateAccountNameError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
        except DuplicateAccountNameError as e:
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
        except DuplicateAccountNameError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/accounts/{id}/

        Soft delete (deactivate) via use case.
        """
        instance = self.get_object()  # DRF handles 404 + 403

        try:
            # Execute use case (soft delete)
            use_case = DeactivateAccount(repository=self.repository, clock=self.clock)
            use_case.execute(account_id=instance.id)

            return Response(status=status.HTTP_204_NO_CONTENT)

        except DomainAccountNotFoundError:
            return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
