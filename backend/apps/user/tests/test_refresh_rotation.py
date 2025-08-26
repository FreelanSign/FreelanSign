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
        # Nettoyer le cache de throttling avant chaque test
        cache.clear()
        self.user = User.objects.create_user(email="john@example.com", password="Secret123!")
        Profile.objects.create(user=self.user)

    def tearDown(self):
        # Nettoyer le cache après chaque test
        cache.clear()

    def test_rotation_blacklists_old_and_returns_new(self):
        # 1) Login
        login_response = self.client.post(LOGIN, {"email": "john@example.com", "password": "Secret123!"}, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        login_data = login_response.json()
        r1 = login_data["refresh"]

        # Vérifier qu'un OutstandingToken a été créé
        outstanding_tokens_count = OutstandingToken.objects.filter(user=self.user).count()
        self.assertGreater(outstanding_tokens_count, 0)

        # 2) Premier refresh → obtient r2 et a1
        refresh_response = self.client.post(REFRESH, {"refresh": r1}, format="json")
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        refresh_data = refresh_response.json()
        self.assertIn("access", refresh_data)
        self.assertIn("refresh", refresh_data)
        r2 = refresh_data["refresh"]

        # Vérifier que r1 a été blacklisté
        r1_outstanding = OutstandingToken.objects.filter(user=self.user).first()
        self.assertTrue(BlacklistedToken.objects.filter(token=r1_outstanding).exists())

        # 3) Réutiliser r1 (ancien) = reuse → 401
        reuse_response = self.client.post(REFRESH, {"refresh": r1}, format="json")
        self.assertEqual(reuse_response.status_code, status.HTTP_401_UNAUTHORIZED)
        error_detail = reuse_response.json().get("detail")
        self.assertIn(error_detail, ["Token reuse detected", "Token is invalid or expired"])

        # # 4) Vérifier que r2 ne fonctionne plus (tous les tokens révoqués)
        # r2_response = self.client.post(REFRESH, {"refresh": r2}, format="json")
        # self.assertEqual(r2_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_invalid_token(self):
        response = self.client.post(REFRESH, {"refresh": "not-a-token"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.json())

    def test_refresh_missing_token(self):
        response = self.client.post(REFRESH, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("refresh", response.json())

    def test_normal_refresh_flow(self):
        # Test du flux normal de refresh sans réutilisation
        login_response = self.client.post(LOGIN, {"email": "john@example.com", "password": "Secret123!"}, format="json")
        r1 = login_response.json()["refresh"]

        # Premier refresh
        refresh1 = self.client.post(REFRESH, {"refresh": r1}, format="json")
        self.assertEqual(refresh1.status_code, status.HTTP_200_OK)
        r2 = refresh1.json()["refresh"]

        # Deuxième refresh avec le nouveau token
        refresh2 = self.client.post(REFRESH, {"refresh": r2}, format="json")
        self.assertEqual(refresh2.status_code, status.HTTP_200_OK)
        r3 = refresh2.json()["refresh"]

        # Le dernier token doit encore fonctionner
        refresh3 = self.client.post(REFRESH, {"refresh": r3}, format="json")
        self.assertEqual(refresh3.status_code, status.HTTP_200_OK)
