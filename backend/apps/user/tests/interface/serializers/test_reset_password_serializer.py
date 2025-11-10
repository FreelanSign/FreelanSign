from urllib.parse import quote

from rest_framework.exceptions import ValidationError

from apps.user.interface.serializers import ResetPasswordSerializer


def test_token_is_url_decoded():
    raw_token = "abc:def:ghi"
    encoded_token = quote(raw_token)  # Simule un lien réel

    serializer = ResetPasswordSerializer(
        data={
            "token": encoded_token,
            "new_password": "Valid123!",
        }
    )

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["token"] == raw_token


def test_serializer_fails_on_missing_fields():
    serializer = ResetPasswordSerializer(data={})
    assert not serializer.is_valid()
    assert "token" in serializer.errors
    assert "new_password" in serializer.errors
