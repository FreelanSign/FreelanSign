from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.client.adapters.persistence.django_client_repository import DjangoClientRepository
from apps.client.application.dto.client_inputs import (
    CreateClientInput,
    DeleteClientInput,
    GetClientInput,
    ListClientsInput,
    UpdateClientInput,
)
from apps.client.application.usecases.create_client import CreateClient
from apps.client.application.usecases.delete_client import DeleteClient
from apps.client.application.usecases.get_client import GetClient
from apps.client.application.usecases.list_clients import ListClients
from apps.client.application.usecases.update_client import UpdateClient
from apps.client.domain.errors import ClientAlreadyExistsError
from apps.client.interface.serializers import (
    ClientCreateInputSerializer,
    ClientListQuerySerializer,
    ClientOutputSerializer,
    ClientUpdateInputSerializer,
)
from apps.client.models import Client
from rest_framework.exceptions import ValidationError


class StandardClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet CRUD fin : délègue aux use cases.
    """

    queryset = Client.objects.all().select_related("owner")
    serializer_class = ClientOutputSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["owner"]
    search_fields = ["name", "email", "phone"]
    ordering_fields = ["created_at", "name"]
    ordering = ["-created_at"]

    # --- Use a single repo instance (stateless) ---
    @property
    def repo(self):
        return DjangoClientRepository()

    # --- List ---
    def list(self, request, *args, **kwargs):
        owner_id = request.query_params.get("owner")
        search = request.query_params.get("search")
        ordering = request.query_params.get("ordering", "-created_at")

        inp = ListClientsInput(
            owner_id=int(owner_id) if owner_id is not None else None,
            search=search,
            ordering=ordering,
        )
        vm = ListClients(self.repo).execute(inp)

        # on réutilise le serializer pour la forme de sortie attendue
        # (mais on pourrait aussi écrire un OutputSerializer)
        # Ici, on repart de la queryset pour profiter de la pagination DRF facilement :
        return super().list(request, *args, **kwargs)

    # --- Retrieve ---
    def retrieve(self, request, *args, **kwargs):
        inp = GetClientInput(client_id=kwargs["pk"])
        vm = GetClient(self.repo).execute(inp)
        if vm is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return super().retrieve(request, *args, **kwargs)

    # --- Create ---
    def create(self, request, *args, **kwargs):
        serializer = ClientCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = getattr(request, "user", None)
        inp = CreateClientInput(
            owner_id=user.id if user else None,
            name=serializer.validated_data.get("name"),
            email=serializer.validated_data.get("email"),
            phone=serializer.validated_data.get("phone"),
            address=serializer.validated_data.get("address"),
            vat_number=serializer.validated_data.get("vat_number"),
            metadata=serializer.validated_data.get("metadata", {}),
        )

        try:
            vm = CreateClient(self.repo).execute(inp)
        except ClientAlreadyExistsError as e:
            raise ValidationError({"name": f"Un client avec le nom '{inp.name}' existe déjà."})

        # Remappe VM → modèle/serializer pour garder la réponse actuelle
        # (option simple: relire l'objet via ORM pour profiter de serializer)
        obj = Client.objects.get(id=vm.id)
        out = ClientOutputSerializer(obj)
        headers = self.get_success_headers(out.data)
        return Response(out.data, status=status.HTTP_201_CREATED, headers=headers)

    # --- Update / Partial update ---
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = ClientUpdateInputSerializer(instance=self.get_object(), data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        inp = UpdateClientInput(
            client_id=str(serializer.instance.id),
            name=serializer.validated_data.get("name") if "name" in serializer.validated_data else None,
            email=serializer.validated_data.get("email") if "email" in serializer.validated_data else None,
            phone=serializer.validated_data.get("phone") if "phone" in serializer.validated_data else None,
            address=serializer.validated_data.get("address") if "address" in serializer.validated_data else None,
            vat_number=serializer.validated_data.get("vat_number") if "vat_number" in serializer.validated_data else None,
            metadata=serializer.validated_data.get("metadata") if "metadata" in serializer.validated_data else None,
        )
        vm = UpdateClient(self.repo).execute(inp)

        # Remappe VM → réponse actuelle
        obj = Client.objects.get(id=vm.id)
        out = ClientOutputSerializer(obj)
        return Response(out.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    # --- Destroy ---
    def destroy(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        DeleteClient(self.repo).execute(DeleteClientInput(client_id=pk))
        return Response(status=status.HTTP_204_NO_CONTENT)
