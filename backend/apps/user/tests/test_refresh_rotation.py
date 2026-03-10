from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase, override_settings
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from apps.user.models import Profile, User

LOGIN = "/api/auth/login/"
REFRESH = "/api/auth/refresh/"


@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
        "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
        "DEFAULT_THROTTLE_CLASSES": [],
        "DEFAULT_THROTTLE_RATES": {},
    }
)
class TestRefreshRotation(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(email="john@example.com", password="Secret123!")
        # Profile created automatically by signal

    def tearDown(self):
        cache.clear()

    def _login(self):
        """Login and return access token; refresh token is set as httpOnly cookie."""
        res = self.client.post(LOGIN, {"email": "john@example.com", "password": "Secret123!"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        return res.json()["access"]

    def test_rotation_blacklists_old_and_returns_new(self):
        # 1) Login — sets fs_refresh cookie
        self._login()
        self.assertIn("fs_refresh", self.client.cookies)

        # Remember the first cookie value
        r1_cookie = self.client.cookies["fs_refresh"].value

        # Verify an OutstandingToken was created
        self.assertGreater(OutstandingToken.objects.filter(user=self.user).count(), 0)

        # 2) First refresh — cookie sent automatically, new cookie received
        refresh_res = self.client.post(REFRESH, {}, format="json")
        self.assertEqual(refresh_res.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_res.json())
        self.assertIn("fs_refresh", self.client.cookies)

        # Verify r1 was blacklisted
        r1_outstanding = OutstandingToken.objects.filter(user=self.user).first()
        self.assertTrue(BlacklistedToken.objects.filter(token=r1_outstanding).exists())

        # 3) Manually set the old cookie value to simulate reuse → 401
        self.client.cookies["fs_refresh"] = r1_cookie
        reuse_res = self.client.post(REFRESH, {}, format="json")
        self.assertEqual(reuse_res.status_code, status.HTTP_401_UNAUTHORIZED)
        error_detail = reuse_res.json().get("detail")
        self.assertIn(error_detail, ["Token reuse detected", "Token is invalid or expired"])

    def test_refresh_invalid_token(self):
        # No valid cookie → 401
        response = self.client.post(REFRESH, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.json())

    def test_refresh_missing_token(self):
        # No cookie at all → 401
        self.client.cookies.clear()
        response = self.client.post(REFRESH, {}, format="json")
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST))

    def test_normal_refresh_flow(self):
        # Login
        self._login()

        # First refresh
        refresh1 = self.client.post(REFRESH, {}, format="json")
        self.assertEqual(refresh1.status_code, status.HTTP_200_OK)

        # Second refresh with rotated cookie
        refresh2 = self.client.post(REFRESH, {}, format="json")
        self.assertEqual(refresh2.status_code, status.HTTP_200_OK)

        # Third refresh
        refresh3 = self.client.post(REFRESH, {}, format="json")
        self.assertEqual(refresh3.status_code, status.HTTP_200_OK)
