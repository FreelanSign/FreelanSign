from rest_framework import serializers

from ..models import User, Profile

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
    # payload d’inscription contract-first
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    profile = ProfileSerializer(required=False)

    # compat legacy (si tu veux encore accepter full_name/phone plats)
    full_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, v):
        return v.strip().lower()
