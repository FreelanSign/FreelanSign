# apps/user/models/models.py
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower

from apps.catalog.models import Area, Prestation


class StatusJuridique(models.TextChoices):
    MICRO = "micro", "Micro-entrepreneur"
    EIRL = "eirl", "EIRL"
    EURL = "eurl", "EURL"
    SASU = "sasu", "SASU"
    OTHER = "other", "Autre"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password=None, **extra_fields):
        """Create and return a user with an email and password."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


# Create your models here.
class User(AbstractUser):
    username = None  # Disable the default username field
    email = models.EmailField("email address", unique=True)  # Use email as the unique identifier
    # We are extending the default Django User model (username, password, email, etc.)
    # We just add phone and full name fields

    # deprecated
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)

    USERNAME_FIELD = "email"  # Set email as the unique identifier for authentication
    REQUIRED_FIELDS = []  # No required fields other than email

    objects = UserManager()  # Use the custom user manager

    class Meta:
        constraints = [UniqueConstraint(Lower("email"), name="uniq_user_email_ci")]


class Profile(models.Model):
    class Role(models.TextChoices):
        FREELANCE = "freelance", "Freelance"
        ADMIN = "admin", "Admin"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.FREELANCE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        base = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return base or f"Profile<{self.user_id}>"


class ProfessionalUser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="professional",
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    status_juridique = models.CharField(max_length=20, choices=StatusJuridique.choices, blank=True, null=True)
    # use lazy string references to avoid circular imports
    domaine = models.ForeignKey("catalog.Area", on_delete=models.SET_NULL, null=True, blank=True, related_name="professionals")
    tjm_cents = models.BigIntegerField(default=0, validators=[MinValueValidator(0)])
    number_pro = models.CharField(max_length=50, blank=True, null=True)  # SIRET / TVA / numéro pro
    service_types = models.ManyToManyField("catalog.Prestation", blank=True, related_name="professionals")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Professional user"
        verbose_name_plural = "Professional users"
        indexes = [
            models.Index(fields=["domaine"]),
            models.Index(fields=["tjm_cents"]),
        ]

    def __str__(self):
        return self.name or f"Professional<{self.user_id}>"

    @property
    def tjm_eur(self):
        return (self.tjm_cents or 0) / 100.0
