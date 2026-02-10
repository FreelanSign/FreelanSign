from rest_framework import status
from rest_framework.test import APITestCase

from apps.user.models import Profile, User

LOGIN = "/api/auth/login/"
REFRESH = "/api/auth/refresh/"
LOGOUT = "/api/auth/logout/"


class TestAuthLogout(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="john@example.com", password="Secret123!")
        # Profile created automatically by signal

        login = self.client.post(LOGIN, {"email": "john@example.com", "password": "Secret123!"}, format="json").json()
        self.access = login["access"]
        self.refresh = login["refresh"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

    def test_logout_blacklists_refresh(self):
        res = self.client.post(LOGOUT, {"refresh": self.refresh}, format="json")
        print(res.status_code, res.content[:200])
        assert res.status_code == status.HTTP_204_NO_CONTENT

        # le même refresh ne doit plus être utilisable
        res2 = self.client.post(REFRESH, {"refresh": self.refresh}, format="json")
        assert res2.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST)

    def test_logout_with_invalid_token_returns_400(self):
        res = self.client.post(LOGOUT, {"refresh": "not-a-token"}, format="json")
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert "refresh" in res.json()
