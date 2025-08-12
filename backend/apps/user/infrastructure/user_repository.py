# adapter to Django's ORM
from ..models.models import User, Profile
from django.db import transaction, IntegrityError
from rest_framework.exceptions import ValidationError


def _split_full_name(full_name: str):
    parts = (full_name or "").strip().split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])

class UserRepository:
    def get_all(self):
        """Retrieve all users."""
        return User.objects.select_related("profile").all()

    @transaction.atomic
    def create(self, **data):
        profile_data = data.pop("profile", {}) or {}

        # Compat: mapper full_name/phone du flat vers profile si fournis
        full_name = data.pop("full_name", None)
        if full_name and not profile_data.get("first_name") and not profile_data.get("last_name"):
            first, last = _split_full_name(full_name)
            profile_data.update({
                "first_name": first,
                "last_name": last,
            })
        legacy_phone = data.pop("phone", None)
        if legacy_phone and not profile_data.get("phone"):
            profile_data["phone"] = legacy_phone

        password = data.pop("password")
        email = data.pop("email").strip().lower()
        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                **data
            )
            Profile.objects.create(user=user, **profile_data)
            return user
        except IntegrityError:
            # Ici on ne dépend pas du nom de contrainte : on renvoie un message champ-par-champ
            raise ValidationError({"email": ["A user with this email already exists."]})

    def get(self, user_id: int):
        """Retrieve a user by ID."""
        return User.objects.select_related("profile").get(pk=user_id)

    def update(self, user_id: int):
        # on limite le update aux profiles
        """Update a user profile."""
        profile_data = user_data.get("profile") or {}
        user = self.get(user_id)
        if profile_data:
            for k, v in profile_data.items():
                setattr(user.profile, k, v)
            user.profile.save()
        return user

    def delete(self, user_id: int):
        """Delete a user by ID."""
        return User.objects.filter(pk=user_id).delete()
