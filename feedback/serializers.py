# Importing serializers from Django REST framework
from rest_framework import serializers
from .models import Feedback  # Importing the Feedback model directly for clarity


class FeedbackSerializer(serializers.ModelSerializer):
    """
    Serializer for the Feedback model.
    Handles serialization and deserialization of Feedback objects.
    """

    # Formatting the created_at field to display in "Month Day Year" format
    created_at: serializers.DateField = serializers.DateField(
        format="%b %d %Y",  # Example: "Jan 01 2023"
        read_only=True  # Ensures this field is not editable
    )

    class Meta:
        """
        Meta class to define model and field configurations for the serializer.
        """
        model: type = Feedback  # Specifying the model to serialize
        fields: str = "__all__"  # Serialize all fields of the model
        # Fields that cannot be modified
        read_only_fields: list[str] = ["user", "created_at"]

    def create(self, validated_data: dict) -> Feedback:
        """
        Override the create method to associate the user with the feedback.
        Args:
            validated_data (dict): Validated data for creating a Feedback instance.
        Returns:
            Feedback: The created Feedback instance.
        """
        # Extracting the user from the request context
        user = self.context["request"].user

        # Merging the user into the validated data
        feedback_data = {**validated_data, "user": user}

        # Handling potential runtime errors during creation
        try:
            return super().create(feedback_data)
        except Exception as e:
            raise serializers.ValidationError(
                f"Error creating feedback: {str(e)}")
