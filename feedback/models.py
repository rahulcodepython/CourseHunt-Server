from django.db import models  # Importing Django's models for database interaction
# Importing the User model for foreign key reference
from authentication.models import User
import uuid  # Importing uuid for generating unique IDs


class Feedback(models.Model):
    """
    Feedback model to store user feedback, ratings, and timestamps.
    Each feedback is linked to a specific user.
    """

    # Primary key for the Feedback model, generated as a unique UUID
    id: str = models.CharField(
        primary_key=True,  # Marks this field as the primary key
        unique=True,  # Ensures the value is unique
        max_length=120,  # Maximum length of the field
        editable=False  # Prevents manual editing
    )

    # Foreign key linking feedback to a user
    user: User = models.ForeignKey(
        User,  # References the User model
        on_delete=models.CASCADE  # Deletes feedback if the user is deleted
    )

    # Text field for storing feedback content
    feedback: str = models.TextField(
        default="",  # Default value is an empty string
        null=True,  # Allows null values
        blank=True  # Allows blank values in forms
    )

    # Integer field for storing user ratings
    rating: int = models.IntegerField(
        default=0  # Default rating is 0
    )

    # Date field for storing the creation timestamp
    created_at: str = models.DateField(
        auto_now_add=True  # Automatically sets the field to the current date on creation
    )

    def __str__(self) -> str:
        """
        Returns the string representation of the Feedback object.
        """
        return self.id

    def save(self, *args, **kwargs) -> None:
        """
        Overrides the save method to handle custom logic before saving the object.
        """
        # Generate a unique ID if it doesn't already exist
        if not self.id:
            self.id = str(uuid.uuid4())

        # Ensure the rating is within the valid range (0 to 5)
        if self.rating < 0:
            self.rating = 0
        elif self.rating > 5:
            self.rating = 5

        # Call the parent class's save method to save the object
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            # Log or handle the exception as needed
            raise RuntimeError(f"An error occurred while saving Feedback: {e}")
