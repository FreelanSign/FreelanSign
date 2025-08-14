from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from apps.user.models import Profile, User

BASE = "/api/user/"
ME = "/api/user/me/"
ME_PROFILE = "/api/user/me/profile/"


@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
        "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
        "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    }
)
class UserApiTests(APITestCase):
    def setUp(self):
        # user "classique" pour les tests /me
        self.user = User.objects.create_user(email="john@example.com", password="Secret123!")
        # Comme on n'a pas de signal post_save, on crée le Profile explicitement si besoin
        if not hasattr(self.user, "profile"):
            Profile.objects.create(user=self.user, first_name="John", last_name="Doe")

        self.token = str(AccessToken.for_user(self.user))

    # ---------- Inscription ----------

    def test_register_user_with_nested_profile(self):
        payload = {
            "email": "jeanne@example.com",
            "password": "Secret123!",
            "profile": {
                "first_name": "Jeanne",
                "last_name": "Dupont",
                "phone": "0712345678",
                "birthday": "1995-06-15",
                "role": "freelance",
                "avatar_url": "https://cdn.test/avatar.png",
            },
        }
        res = self.client.post(BASE, data=payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        body = res.json()
        self.assertIn("id", body)
        self.assertEqual(body["email"], "jeanne@example.com")
        self.assertIn("profile", body)
        self.assertEqual(body["profile"]["first_name"], "Jeanne")
        self.assertEqual(body["profile"]["last_name"], "Dupont")

    def test_register_user_legacy_full_name_phone(self):
        payload = {"email": "legacy@example.com", "password": "Secret123!", "full_name": "Marie Curie", "phone": "0600000000"}
        res = self.client.post(BASE, data=payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        body = res.json()
        self.assertEqual(body["email"], "legacy@example.com")
        self.assertEqual(body["profile"]["first_name"], "Marie")
        self.assertEqual(body["profile"]["last_name"], "Curie")
        self.assertEqual(body["profile"]["phone"], "0600000000")

    # ---------- /me ----------

    def test_me_requires_auth(self):
        res = self.client.get(ME)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_authenticated_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        res = self.client.get(ME)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        body = res.json()
        self.assertEqual(body["email"], "john@example.com")
        self.assertIn("profile", body)
        self.assertEqual(body["profile"]["first_name"], "John")

    # ---------- PATCH /me/profile ----------

    def test_update_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        patch = {"first_name": "Johnny", "avatar_url": "https://cdn.test/john.png"}
        res = self.client.patch(ME_PROFILE, data=patch, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        body = res.json()
        # On a choisi de renvoyer UserSerializer, donc profil inclus
        self.assertEqual(body["profile"]["first_name"], "Johnny")
        self.assertTrue(body["profile"]["avatar_url"].endswith("john.png"))

    def test_register_duplicate_email_returns_400(self):
        payload = {"email": "john@example.com", "password": "Secret123!"}
        # user initial créé en setUp()
        res = self.client.post("/api/user/", data=payload, format="json")
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in res.json()
