# apps/user/interface/serializers.py
import logging

from django.apps import apps
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from apps.catalog.models import Area, Prestation
from apps.user.models.models import ProfessionalUser

from ..models import Profile, User

logger = logging.getLogger("apps.user.serializers")


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "birthday", "phone", "avatar_url", "role"]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "birthday", "phone", "avatar_url", "role"]
        extra_kwargs = {
            "role": {"required": False},
        }


class UserSerializer(serializers.ModelSerializer):
    # lecture : on expose le profil
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "profile"]  # on n’expose plus full_name/phone ici
        read_only_fields = ["id", "email"]


class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="A user with this email already exists.")]
    )
    password = serializers.CharField(write_only=True)
    profile = ProfileSerializer(required=False)
    full_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, v):
        cleaned = v.strip().lower()
        logger.debug("UserRegistrationSerializer.validate_email -> %s", cleaned)
        return cleaned


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ProfessionalUserSerializer(serializers.ModelSerializer):
    service_types = serializers.ListField(child=serializers.IntegerField(), required=False)
    domaine = serializers.IntegerField(allow_null=True, required=False)

    class Meta:
        model = ProfessionalUser
        fields = (
            "id",
            "user",
            "name",
            "status_juridique",
            "domaine",
            "tjm_cents",
            "number_pro",
            "service_types",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("user", "created_at", "updated_at")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Prestation = apps.get_model("catalog", "Prestation")
        Area = apps.get_model("catalog", "Area")
        self.fields["service_types"] = serializers.PrimaryKeyRelatedField(
            queryset=Prestation.objects.all(), many=True, required=False
        )
        self.fields["domaine"] = serializers.PrimaryKeyRelatedField(
            queryset=Area.objects.all(), allow_null=True, required=False
        )

    def create(self, validated_data):
        service_types = validated_data.pop("service_types", [])
        request = self.context.get("request")
        user_id = getattr(request.user, "id", None) if request else None
        logger.info("ProfessionalUserSerializer.create called user_id=%s", user_id)
        if not request or not getattr(request, "user", None) or not request.user.is_authenticated:
            logger.warning("ProfessionalUserSerializer.create denied - unauthenticated")
            raise ValidationError("Authenticated user required to create a ProfessionalUser.")
        user = request.user
        try:
            prof = ProfessionalUser.objects.create(user=user, **validated_data)
            if service_types:
                prof.service_types.set(service_types)
            logger.info("ProfessionalUserSerializer.create succeeded professional_id=%s user_id=%s", prof.id, user_id)
            return prof
        except Exception:
            logger.exception("ProfessionalUserSerializer.create failed for user_id=%s", user_id)
            raise

    def update(self, instance, validated_data):
        service_types = validated_data.pop("service_types", None)
        logger.info("ProfessionalUserSerializer.update called professional_id=%s", getattr(instance, "id", None))
        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            if service_types is not None:
                instance.service_types.set(service_types)
            logger.info("ProfessionalUserSerializer.update succeeded professional_id=%s", instance.id)
            return instance
        except Exception:
            logger.exception("ProfessionalUserSerializer.update failed professional_id=%s", getattr(instance, "id", None))
            raise
