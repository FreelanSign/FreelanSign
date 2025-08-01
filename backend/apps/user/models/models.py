from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    username = None  # Disable the default username field
    email = models.EmailField(
        "email address", unique=True
    )  # Use email as the unique identifier
    # We are extending the default Django User model (username, password, email, etc.)
    # We just add phone and full name fields
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)

    USERNAME_FIELD = "email"  # Set email as the unique identifier for authentication
    REQUIRED_FIELDS = []  # No required fields other than email
