# For PostgreSQL-specific array fields
from django.contrib.postgres.fields import ArrayField
from django.db import models  # Django ORM models
# Importing User model for ForeignKey relation
from authentication.models import User
import uuid  # For generating unique IDs


class Course(models.Model):
    """
    Represents a course with various attributes such as name, description, price, language, tags, and more.
    Includes metadata like creation date and creator.
    """

    # Primary key for the course, auto-generated as a UUID
    id: str = models.CharField(
        primary_key=True, unique=True, max_length=120, editable=False
    )

    # Basic course details
    name: str = models.CharField(
        default="", max_length=120, null=True, blank=True
    )  # Course name
    short_description: str = models.TextField(
        default="", null=True, blank=True
    )  # Short description of the course
    long_description: str = models.TextField(
        default="", null=True, blank=True
    )  # Detailed description of the course

    # Pricing and metadata
    price: int = models.IntegerField(default=0)  # Price of the course
    created_at: models.DateTimeField = models.DateField(
        auto_now_add=True
    )  # Auto-generated creation date
    created_by: User = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # Reference to the user who created the course

    # Course attributes
    language_choices: list[tuple[str, str]] = [
        ("en", "English"),
        ("es", "Spanish"),
        ("fr", "French"),
    ]  # Example language choices
    language: list[str] = ArrayField(
        models.CharField(max_length=10, blank=True),
        size=3,
        default=list,
        null=True,
        blank=True,
    )  # Supported languages for the course

    rating: float = models.FloatField(default=0.0)  # Course rating
    learners: int = models.IntegerField(
        default=0)  # Number of learners enrolled

    # Tags for categorization
    tags: list[str] = ArrayField(
        models.CharField(max_length=50, blank=True),
        size=10,
        default=list,
        null=True,
        blank=True,
    )

    # Discounts and duration
    # Discount offer on the course
    offer: float = models.FloatField(default=0.0)
    duration: str = models.CharField(
        default="", max_length=50, null=True, blank=True
    )  # Duration of the course

    # Media and resources
    thumbnail: str = models.CharField(
        max_length=1000, default="", null=True, blank=True
    )  # Thumbnail image URL
    status_choices: list[tuple[str, str]] = [
        ("draft", "Draft"),
        ("published", "Published"),
    ]  # Status choices for the course
    status: str = models.CharField(
        max_length=50, choices=status_choices, default="draft"
    )  # Current status of the course

    # URLs for additional resources
    videoURL: str = models.CharField(
        default="", max_length=1000, blank=True, null=True
    )  # Video URL
    notesURL: str = models.CharField(
        default="", max_length=1000, blank=True, null=True
    )  # Notes URL
    presentationURL: str = models.CharField(
        default="", max_length=1000, blank=True, null=True
    )  # Presentation URL
    codeURL: str = models.CharField(
        default="", max_length=1000, blank=True, null=True
    )  # Code repository URL

    # Additional content and requirements
    content: str = models.TextField(
        default="", null=True, blank=True
    )  # Course content
    includes: list[str] = ArrayField(
        models.CharField(max_length=1000, blank=True, null=True),
        size=10,
        default=list,
        null=True,
        blank=True,
    )  # What the course includes
    requirements: list[str] = ArrayField(
        models.CharField(max_length=1000, blank=True, null=True),
        size=10,
        default=list,
        null=True,
        blank=True,
    )  # Requirements for taking the course

    def __str__(self) -> str:
        """
        Returns the string representation of the course.
        """
        return self.name

    def save(self, *args, **kwargs) -> None:
        """
        Overrides the save method to auto-generate a UUID for the course ID if not provided.
        """
        if not self.id:  # Check if the ID is not already set
            self.id = str(uuid.uuid4())  # Generate a new UUID

        try:
            # Call the parent save method
            super(Course, self).save(*args, **kwargs)
        except Exception as e:
            # Handle runtime errors
            raise RuntimeError(f"Error saving Course: {e}")
