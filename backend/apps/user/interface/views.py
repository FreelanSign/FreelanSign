# apps/user/interface/views.py
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import decorators, permissions, response, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.infrastructure.user_repository import UserRepository
from apps.user.interface.serializers import (
    ChangePasswordSerializer,
    LogoutSerializer,
    ProfessionalUserSerializer,
    ProfileUpdateSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)
from apps.user.models.models import ProfessionalUser
from apps.user.services.user_service import UserService


@extend_schema_view(
    list=extend_schema(summary="List all users", responses={200: OpenApiResponse(UserSerializer(many=True))}, tags=["Users"]),
    create=extend_schema(
        summary="Register a new user",
        request=UserRegistrationSerializer,
        responses={201: OpenApiResponse(UserSerializer)},
        tags=["Users"],
    ),
    me=extend_schema(
        summary="Get current authenticated user", responses={200: OpenApiResponse(UserSerializer)}, tags=["Users"]
    ),
    update_me_profile=extend_schema(
        summary="Update profile of current user",
        request=ProfileUpdateSerializer,
        responses={200: OpenApiResponse(UserSerializer)},
        tags=["Users"],
    ),
    change_password=extend_schema(
        summary="Change password for current user",
        request=ChangePasswordSerializer,
        responses={204: OpenApiResponse({"detail": "Password changed successfully"})},
        tags=["Users"],
    ),
)
class UserViewSet(viewsets.ViewSet):
    service = UserService(user_repository=UserRepository())

    def get_permissions(self):
        if self.action in ["create", "list"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(responses=UserSerializer(many=True))
    def list(self, request):
        users = self.service.list_users()
        return Response(UserSerializer(users, many=True).data)

    @extend_schema(request=UserRegistrationSerializer, responses={201: UserSerializer}, summary="Register a new user")
    def create(self, request):
        reg = UserRegistrationSerializer(data=request.data)
        reg.is_valid(raise_exception=True)
        user = self.service.register_user(**reg.validated_data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="me", permission_classes=[IsAuthenticated])
    @extend_schema(responses=UserSerializer, summary="Get current authenticated user")
    def me(self, request):
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=["patch"], url_path="me/profile", permission_classes=[IsAuthenticated])
    @extend_schema(request=ProfileUpdateSerializer, responses=UserSerializer, summary="Update profile of current user")
    def update_me_profile(self, request):
        ser = ProfileUpdateSerializer(request.user.profile, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=["post"], url_path="me/change-password", permission_classes=[IsAuthenticated])
    def change_password(self, request):
        ser = ChangePasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(ser.validated_data["current_password"]):
            return Response({"current_password": "Incorrect password"}, status=400)
        user.set_password(ser.validated_data["new_password"])
        user.save()
        return Response({"detail": "Password changed successfully"}, status=204)


class ProfessionalUserMeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(ProfessionalUserSerializer),
            404: OpenApiResponse(description="Professional profile not found."),
        },
        summary="Get professional profile for current authenticated user",
        tags=["Professional Users"],
    )
    def get(self, request):
        prof = getattr(request.user, "professional", None)
        if not prof:
            return Response({"detail": "Professional profile not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfessionalUserSerializer(prof, context={"request": request})
        return Response(serializer.data)

    @extend_schema(
        request=ProfessionalUserSerializer,
        responses={200: OpenApiResponse(ProfessionalUserSerializer)},
        summary="Patch (create if missing) professional profile for current user",
        tags=["Professional Users"],
    )
    def patch(self, request):
        prof = getattr(request.user, "professional", None)
        if not prof:
            # create if missing
            serializer = ProfessionalUserSerializer(data=request.data, context={"request": request})
        else:
            serializer = ProfessionalUserSerializer(prof, data=request.data, partial=True, context={"request": request})

        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response(ProfessionalUserSerializer(obj, context={"request": request}).data, status=status.HTTP_200_OK)


class OnboardingProfessionalView(APIView):
    """
    Endpoint to create the professional entity during onboarding.
    POST allowed for authenticated users; admins could have list/create elsewhere.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ProfessionalUserSerializer,
        responses={
            201: OpenApiResponse(ProfessionalUserSerializer),
            200: OpenApiResponse(ProfessionalUserSerializer),
        },
        summary="Create or update professional entity during onboarding",
        tags=["Professional Users"],
    )
    def post(self, request):
        try:
            prof = request.user.professional
        except ObjectDoesNotExist:
            prof = None
        if prof:
            serializer = ProfessionalUserSerializer(prof, data=request.data, partial=True, context={"request": request})
        else:
            serializer = ProfessionalUserSerializer(data=request.data, context={"request": request})

        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response(
            ProfessionalUserSerializer(obj, context={"request": request}).data,
            status=status.HTTP_201_CREATED if not prof else status.HTTP_200_OK,
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allow access only to staff (admin) or the owner of the object.

    Important behaviour:
    - For the ViewSet `list` action we explicitly only allow staff members (non-admins will receive 403).
    - For other actions, authenticated users are allowed at the permission level; object-level ownership is enforced in `has_object_permission`.
    """

    def has_permission(self, request, view):
        # Deny unauthenticated users globally
        if not request.user or not request.user.is_authenticated:
            return False
        # Only staff may list all ProfessionalUser objects
        if getattr(view, "action", None) == "list":
            return request.user.is_staff
        # Otherwise allow and let has_object_permission enforce ownership for object-level actions
        return True

    def has_object_permission(self, request, view, obj):
        # Allow staff to access any object
        if request.user and request.user.is_staff:
            return True
        # Otherwise only the owner may access
        return getattr(obj, "user", None) == request.user


class ProfessionalUserViewSet(viewsets.ModelViewSet):
    """
    CRUD pour ProfessionalUser.
    - Les non-admins ne voient que leur ressource (queryset filtré).
    - Les admins voient tout.
    """

    serializer_class = ProfessionalUserSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        qs = ProfessionalUser.objects.all().select_related("user", "domaine").prefetch_related("service_types")
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        # forcer la liaison à l'utilisateur courant
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        # si tu souhaites soft-delete, remplace par instance.soft_delete() ou similar
        instance.delete()

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        GET /api/professional/me/  -> renvoie l'objet du user courant (même comportement que l'ancien /professional/me/)
        """
        prof = getattr(request.user, "professional", None)
        if not prof:
            return Response({"detail": "Professional profile not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(prof)
        return Response(serializer.data)
