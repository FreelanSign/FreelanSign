# apps/feedback/interface/views.py
import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.feedback.adapters.django_feedback_repository import DjangoFeedbackRepository
from apps.feedback.application.dtos import CreateFeedbackInput
from apps.feedback.application.usecases.create_feedback import CreateFeedback
from apps.feedback.domain.policies import InvalidCategoryError, InvalidMessageLengthError
from apps.feedback.interface.serializers import CreateFeedbackSerializer
from config import settings

logger = logging.getLogger(__name__)


@extend_schema(tags=["Feedback"])
class CreateFeedbackView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "feedback"

    @extend_schema(
        summary="Submit feedback",
        request=CreateFeedbackSerializer,
        responses={201: None, 400: None, 429: None},
    )
    def post(self, request):
        ser = CreateFeedbackSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        page_url = request.META.get("HTTP_REFERER", "")
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        app_version = getattr(settings, "SPECTACULAR_SETTINGS", {}).get("VERSION", "unknown")

        input_dto = CreateFeedbackInput(
            category=ser.validated_data["category"],
            message=ser.validated_data["message"],
            user_email=request.user.email,
            page_url=page_url,
            app_version=app_version,
            user_agent=user_agent,
        )

        try:
            use_case = CreateFeedback(
                feedback_repository=DjangoFeedbackRepository(),
            )
            use_case.execute(user_id=request.user.id, input_dto=input_dto)
            return Response({"detail": "Feedback submitted."}, status=status.HTTP_201_CREATED)

        except (InvalidMessageLengthError, InvalidCategoryError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
