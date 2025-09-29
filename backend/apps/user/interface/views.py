# apps/user/interface/views.py
import logging

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

logger = logging.getLogger("apps.user.views")


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
        logger.info("users.list called", extra={"user_id": getattr(request.user, "id", None)})
        users = self.service.list_users()
        logger.debug("users.list returning %d users", len(users))
        return Response(UserSerializer(users, many=True).data)

    @extend_schema(request=UserRegistrationSerializer, responses={201: UserSerializer}, summary="Register a new user")
    def create(self, request):
        logger.info("users.create called", extra={"params": {k: v for k, v in request.data.items() if k != "password"}})
        reg = UserRegistrationSerializer(data=request.data)
        try:
            reg.is_valid(raise_exception=True)
        except Exception as e:
            logger.warning("users.create validation failed: %s", reg.errors)
            raise
        user = self.service.register_user(**reg.validated_data)
        logger.info("users.create succeeded for user_id=%s", getattr(user, "id", None))
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="me", permission_classes=[IsAuthenticated])
    @extend_schema(responses=UserSerializer, summary="Get current authenticated user")
    def me(self, request):
        logger.debug("users.me called", extra={"user_id": request.user.id})
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=["patch"], url_path="me/profile", permission_classes=[IsAuthenticated])
    @extend_schema(request=ProfileUpdateSerializer, responses=UserSerializer, summary="Update profile of current user")
    def update_me_profile(self, request):
        logger.info("users.update_me_profile called", extra={"user_id": request.user.id, "params": request.data})
        ser = ProfileUpdateSerializer(request.user.profile, data=request.data, partial=True)
        try:
            ser.is_valid(raise_exception=True)
            ser.save()
        except Exception:
            logger.exception("users.update_me_profile failed for user_id=%s", request.user.id)
            raise
        logger.info("users.update_me_profile succeeded for user_id=%s", request.user.id)
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=["post"], url_path="me/change-password", permission_classes=[IsAuthenticated])
    def change_password(self, request):
        logger.info("change_password called", extra={"user_id": request.user.id})
        ser = ChangePasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(ser.validated_data["current_password"]):
            logger.warning("change_password incorrect current_password for user_id=%s", user.id)
            return Response({"current_password": "Incorrect password"}, status=400)
        user.set_password(ser.validated_data["new_password"])
        user.save()
        logger.info("change_password succeeded for user_id=%s", user.id)
        return Response({"detail": "Password changed successfully"}, status=204)


class ProfessionalUserMeView(APIView):
    permission_classes = [IsAuthenticated]
    logger = logging.getLogger("apps.user.views.ProfessionalUserMeView")

    @extend_schema(
        responses={
            200: OpenApiResponse(ProfessionalUserSerializer),
            404: OpenApiResponse(description="Professional profile not found."),
        },
        summary="Get professional profile for current authenticated user",
        tags=["Professional Users"],
    )
    def get(self, request):
        logger.info("ProfessionalUserMeView.get called", extra={"user_id": request.user.id})
        prof = getattr(request.user, "professional", None)
        if not prof:
            logger.debug("ProfessionalUserMeView.get: no professional for user_id=%s", request.user.id)
            return Response({"detail": "Professional profile not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfessionalUserSerializer(prof, context={"request": request})
        logger.debug("ProfessionalUserMeView.get: returning professional id=%s", prof.id)
        return Response(serializer.data)

    @extend_schema(
        request=ProfessionalUserSerializer,
        responses={200: OpenApiResponse(ProfessionalUserSerializer)},
        summary="Patch (create if missing) professional profile for current user",
        tags=["Professional Users"],
    )
    def patch(self, request):
        logger.info("ProfessionalUserMeView.patch called", extra={"user_id": request.user.id, "params": request.data})
        prof = getattr(request.user, "professional", None)
        if not prof:
            serializer = ProfessionalUserSerializer(data=request.data, context={"request": request})
            action = "create"
        else:
            serializer = ProfessionalUserSerializer(prof, data=request.data, partial=True, context={"request": request})
            action = "update"

        try:
            serializer.is_valid(raise_exception=True)
            obj = serializer.save()
        except Exception:
            logger.exception("ProfessionalUserMeView.patch failed for user_id=%s", request.user.id)
            raise

        logger.info(
            "ProfessionalUserMeView.patch %s succeeded for professional_id=%s user_id=%s",
            action,
            getattr(obj, "id", None),
            request.user.id,
        )
        return Response(ProfessionalUserSerializer(obj, context={"request": request}).data, status=status.HTTP_200_OK)


class OnboardingProfessionalView(APIView):
    permission_classes = [IsAuthenticated]
    logger = logging.getLogger("apps.user.views.OnboardingProfessionalView")

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
        logger.info("OnboardingProfessionalView.post called", extra={"user_id": request.user.id, "params": request.data})
        try:
            prof = request.user.professional
        except ObjectDoesNotExist:
            prof = None
        if prof:
            serializer = ProfessionalUserSerializer(prof, data=request.data, partial=True, context={"request": request})
            status_code = status.HTTP_200_OK
            action = "update"
        else:
            serializer = ProfessionalUserSerializer(data=request.data, context={"request": request})
            status_code = status.HTTP_201_CREATED
            action = "create"

        try:
            serializer.is_valid(raise_exception=True)
            obj = serializer.save()
        except Exception:
            logger.exception("OnboardingProfessionalView.post failed for user_id=%s", request.user.id)
            raise

        logger.info(
            "OnboardingProfessionalView.post %s succeeded professional_id=%s user_id=%s",
            action,
            getattr(obj, "id", None),
            request.user.id,
        )
        return Response(ProfessionalUserSerializer(obj, context={"request": request}).data, status=status_code)


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            logger.debug("IsOwnerOrAdmin.has_permission denied unauthenticated request")
            return False
        if getattr(view, "action", None) == "list":
            allowed = request.user.is_staff
            logger.debug("IsOwnerOrAdmin.has_permission for list -> is_staff=%s", request.user.is_staff)
            return allowed
        return True

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            logger.debug("IsOwnerOrAdmin.has_object_permission allowed for staff user_id=%s", request.user.id)
            return True
        owner = getattr(obj, "user", None)
        allowed = owner == request.user
        logger.debug(
            "IsOwnerOrAdmin.has_object_permission owner=%s user=%s allowed=%s",
            getattr(owner, "id", None),
            request.user.id,
            allowed,
        )
        return allowed


class ProfessionalUserViewSet(viewsets.ModelViewSet):
    serializer_class = ProfessionalUserSerializer
    permission_classes = [IsOwnerOrAdmin]
    logger = logging.getLogger("apps.user.views.ProfessionalUserViewSet")

    def get_queryset(self):
        self.logger.debug("ProfessionalUserViewSet.get_queryset called user_id=%s", getattr(self.request.user, "id", None))
        qs = ProfessionalUser.objects.all().select_related("user", "domaine").prefetch_related("service_types")
        if self.request.user.is_staff:
            self.logger.debug("ProfessionalUserViewSet.get_queryset returning full queryset for staff user")
            return qs
        self.logger.debug("ProfessionalUserViewSet.get_queryset filtering by user=%s", self.request.user.id)
        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        self.logger.info("ProfessionalUserViewSet.perform_create called user_id=%s", getattr(self.request.user, "id", None))
        serializer.save(user=self.request.user)
        self.logger.info(
            "ProfessionalUserViewSet.perform_create finished saved professional for user_id=%s", self.request.user.id
        )

    def perform_destroy(self, instance):
        self.logger.info("ProfessionalUserViewSet.perform_destroy called professional_id=%s", getattr(instance, "id", None))
        instance.delete()
        self.logger.info("ProfessionalUserViewSet.perform_destroy finished professional_id=%s", getattr(instance, "id", None))

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        self.logger.debug("ProfessionalUserViewSet.me called user_id=%s", request.user.id)
        prof = getattr(request.user, "professional", None)
        if not prof:
            self.logger.debug("ProfessionalUserViewSet.me: professional not found for user_id=%s", request.user.id)
            return Response({"detail": "Professional profile not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(prof)
        return Response(serializer.data)
