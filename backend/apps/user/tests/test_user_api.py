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
        # user "classique" pour tests /me
        self.user = User.objects.create_user(email="john@example.com", password="Secret123!")
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
        # rôle créé par défaut/forcé côté back
        self.assertEqual(body["profile"]["role"], "freelance")

    def test_register_user_legacy_full_name_phone(self):
        payload = {
            "email": "legacy@example.com",
            "password": "Secret123!",
            "full_name": "Marie Curie",
            "phone": "0600000000",
        }
        res = self.client.post(BASE, data=payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        body = res.json()
        self.assertEqual(body["email"], "legacy@example.com")
        self.assertEqual(body["profile"]["first_name"], "Marie")
        self.assertEqual(body["profile"]["last_name"], "Curie")
        self.assertEqual(body["profile"]["phone"], "0600000000")
        self.assertEqual(body["profile"]["role"], "freelance")

    def test_register_defaults_to_freelance_when_role_missing(self):
        payload = {
            "email": "no_role@example.com",
            "password": "Secret123!",
            "profile": {"first_name": "Nora", "last_name": "Ole"},
        }
        res = self.client.post(BASE, data=payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.json()["profile"]["role"], "freelance")

    def test_register_attempt_admin_forced_to_freelance_and_logs_warning(self):
        payload = {
            "email": "wannabe.admin@example.com",
            "password": "Secret123!",
            "profile": {"first_name": "Wanna", "last_name": "Admin", "role": "admin"},
        }
        # capture le warning logger si tu as laissé un logger.warning côté serializer
        with self.assertLogs("apps.user", level="WARNING") as cm:
            res = self.client.post(BASE, data=payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        body = res.json()
        self.assertEqual(body["profile"]["role"], "freelance")
        # optionnel : assert qu'on a bien loggé quelque chose
        joined = "\n".join(cm.output)
        self.assertIn("self-register as admin", joined)

    def test_register_duplicate_email_returns_400(self):
        payload = {"email": "john@example.com", "password": "Secret123!"}
        res = self.client.post(BASE, data=payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", res.json())

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

    def test_update_profile_basic_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        patch = {"first_name": "Johnny", "avatar_url": "https://cdn.test/john.png"}
        res = self.client.patch(ME_PROFILE, data=patch, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        body = res.json()
        # on renvoie UserSerializer (avec profil)
        self.assertEqual(body["profile"]["first_name"], "Johnny")
        self.assertTrue(body["profile"]["avatar_url"].endswith("john.png"))
        # rôle resté freelance
        self.assertEqual(body["profile"]["role"], "freelance")

    def test_non_staff_cannot_promote_self_to_admin_role_is_ignored(self):
        """
        Avec ProfileUpdateSerializer.get_fields() qui met role en read_only pour non-staff,
        le champ est ignoré et le rôle reste 'freelance'.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        res1 = self.client.get(ME)
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(res1.json()["profile"]["role"], "freelance")

        # tentative de promotion
        res = self.client.patch(ME_PROFILE, data={"role": "admin"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        body = res.json()
        self.assertEqual(body["profile"]["role"], "freelance")

    def test_staff_can_set_admin_role_on_self(self):
        """
        Si tu autorises les staff à modifier leur propre rôle via /me/profile/,
        ce test vérifie que ça passe à 'admin'.
        """
        staff = User.objects.create_user(email="staff@example.com", password="Secret123!", is_staff=True)
        if not hasattr(staff, "profile"):
            Profile.objects.create(user=staff, first_name="Staff", last_name="User")
        staff_token = str(AccessToken.for_user(staff))

        # sanity check
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {staff_token}")
        res0 = self.client.get(ME)
        self.assertEqual(res0.status_code, status.HTTP_200_OK)
        self.assertEqual(res0.json()["profile"]["role"], "freelance")

        # promotion -> admin
        res = self.client.patch(ME_PROFILE, data={"role": "admin"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        body = res.json()
        self.assertEqual(body["profile"]["role"], "admin")
