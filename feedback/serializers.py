from rest_framework import serializers
from . import models


class FeedbackSerializer(serializers.ModelSerializer):
    created_at = serializers.DateField(format="%b %d %Y", read_only=True)

    class Meta:
        model = models.Feedback
        fields = "__all__"
        read_only_fields = ["user", "created_at"]

    def create(self, validated_data):
        return super().create({**validated_data, "user": self.context["request"].user})
