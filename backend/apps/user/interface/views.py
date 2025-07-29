# apps/user/interface/views.py
from rest_framework.response import Response
from rest_framework import viewsets
from apps.user.services.user_service import UserService
from apps.user.infrastructure.user_repository import UserRepository
from apps.user.interface.serializers import UserSerializer

class UserViewSet(viewsets.ViewSet):
    service = UserService(user_repository=UserRepository())

    def list(self, request):
        users = self.service.list_users()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def create(self, request):
        user = self.service.register_user(**request.data)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=201)
