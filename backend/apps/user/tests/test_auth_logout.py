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

        # Login: refresh token set as httpOnly cookie (not in body)
        login_res = self.client.post(LOGIN, {"email": "john@example.com", "password": "Secret123!"}, format="json")
        self.access = login_res.json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

    def test_logout_blacklists_refresh(self):
        # Cookie sent automatically; no body needed
        res = self.client.post(LOGOUT, {}, format="json")
        assert res.status_code == status.HTTP_204_NO_CONTENT

        # Refresh cookie cleared after logout — subsequent refresh should fail
        res2 = self.client.post(REFRESH, {}, format="json")
        assert res2.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST)

    def test_logout_with_invalid_token_returns_204(self):
        # Logout is idempotent: no cookie → still returns 204
        self.client.cookies.clear()
        res = self.client.post(LOGOUT, {}, format="json")
        assert res.status_code == status.HTTP_204_NO_CONTENT
