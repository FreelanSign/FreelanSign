from rest_framework import serializers
from ..models import User

class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'phone', 'password']
        read_only_fields = ['id']
