# apps/feedback/interface/serializers.py
from rest_framework import serializers

from apps.feedback.domain.entities import FeedbackCategory


class CreateFeedbackSerializer(serializers.Serializer):
    category = serializers.ChoiceField(choices=[(c.value, c.value) for c in FeedbackCategory])
    message = serializers.CharField(min_length=10, max_length=2000)
