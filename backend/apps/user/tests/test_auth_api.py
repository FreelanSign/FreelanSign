from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Profile, User

LOGIN = "/api/auth/login/"
REFRESH = "/api/auth/refresh/"


class TestAuthApi(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="john@example.com", password="password123")
        # Profile created automatically by signal

    def test_login_success_returns_access_token_and_sets_cookie(self):
        res = self.client.post(LOGIN, {"email": "john@example.com", "password": "password123"}, format="json")
        assert res.status_code == status.HTTP_200_OK
        body = res.json()
        # Access token in body; refresh token as httpOnly cookie (not in body)
        assert "access" in body
        assert "refresh" not in body
        assert "fs_refresh" in res.cookies

    def test_login_wrong_password_401(self):
        res = self.client.post(LOGIN, {"email": "john@example.com", "password": "wrong!"}, format="json")
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_success_returns_new_access(self):
        # Login to get the httpOnly cookie set
        self.client.post(LOGIN, {"email": "john@example.com", "password": "password123"}, format="json")
        # Refresh using cookie (sent automatically by test client)
        res = self.client.post(REFRESH, {}, format="json")
        assert res.status_code == status.HTTP_200_OK
        assert "access" in res.json()

    def test_refresh_invalid_token_401(self):
        res = self.client.post(REFRESH, {}, format="json")
        assert res.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST)
