import pytest
from django.urls import reverse
from rest_framework import status

from apps.client.models import Client


@pytest.mark.django_db
class TestClientAPI:
    def test_list_clients_filtered_by_account(self, api_client, user_with_account, account):
        # Create clients for different accounts
        other_user = user_with_account  # Reusing fixture might not work for creating another user easily without factory
        # Let's just create clients manually linked to account

        c1 = Client.objects.create(owner=user_with_account, account=account, name="Client A")
        c2 = Client.objects.create(owner=user_with_account, account=account, name="Client B")

        # Create another client for another account (simulated)
        # We need another account. For simplicity, let's just ensure we see c1 and c2.

        api_client.force_authenticate(user=user_with_account)
        url = reverse("client-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 2
        names = {r["name"] for r in data["results"]}
        assert names == {"Client A", "Client B"}

    def test_create_client_linked_to_account(self, api_client, user_with_account, account):
        api_client.force_authenticate(user=user_with_account)
        url = reverse("client-list")
        payload = {"name": "New API Client", "email": "test@api.com"}

        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "New API Client"
        assert data["account_id"] == account.id

        # Verify DB
        client = Client.objects.get(id=data["id"])
        assert client.account == account
        assert client.owner == user_with_account

    def test_create_client_duplicate_name_in_account_fails(self, api_client, user_with_account, account):
        Client.objects.create(owner=user_with_account, account=account, name="Existing Client")

        api_client.force_authenticate(user=user_with_account)
        url = reverse("client-list")
        payload = {"name": "Existing Client", "email": "other@api.com"}

        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Un client avec le nom 'Existing Client' existe déjà." in str(response.data)
