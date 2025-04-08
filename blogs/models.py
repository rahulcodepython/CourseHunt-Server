from django.db import models  # Importing Django's models for ORM
# Importing User model for relationships
from authentication.models import User
import uuid  # Importing uuid for generating unique IDs

# Blog model to represent blog posts


class Blog(models.Model):
    """
    Represents a blog post with attributes like title, content, image, likes, and comments.
    """

    # Primary key for the Blog model, generated using UUID
    id: str = models.CharField(
        max_length=100, primary_key=True, unique=True, editable=False, db_index=True
    )

    # Title of the blog
    title: str = models.CharField(max_length=100)

    # Content of the blog
    content: str = models.TextField()

    # URL or path to the blog's image
    image: str = models.CharField(max_length=1000)

    # Timestamp for when the blog was created
    created_at: models.DateField = models.DateField(auto_now_add=True)

    # Timestamp for when the blog was last updated
    updated_at: models.DateField = models.DateField(auto_now=True)

    # Number of likes on the blog
    likes: int = models.IntegerField(default=0)

    # Many-to-Many relationship with User for likes
    like: models.ManyToManyField = models.ManyToManyField(
        User, related_name="liked_blogs", blank=True
    )

    # Number of times the blog has been read
    read: int = models.IntegerField(default=0)

    # Number of comments on the blog
    comments: int = models.IntegerField(default=0)

    def __str__(self) -> str:
        """
        Returns the string representation of the blog.
        """
        return self.title

    def save(self, *args, **kwargs) -> None:
        """
        Overrides the save method to generate a UUID for the blog ID if not already set.
        """
        if not self.id:  # Check if the ID is not set
            self.id = str(uuid.uuid4())  # Generate a unique UUID
        super().save(*args, **kwargs)  # Call the parent class's save method


# Comment model to represent comments on blogs
class Comment(models.Model):
    """
    Represents a comment on a blog post, with support for nested comments.
    """

    # Primary key for the Comment model, generated using UUID
    id: str = models.CharField(
        max_length=100, primary_key=True, unique=True, editable=False, db_index=True
    )

    # Foreign key to the User who made the comment
    user: User = models.ForeignKey(User, on_delete=models.CASCADE)

    # Foreign key to the Blog the comment belongs to
    blog: Blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

    # Foreign key to the parent comment for nested comments
    parent: "Comment" = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )

    # Content of the comment
    content: str = models.TextField()

    # Timestamp for when the comment was created
    created_at: models.DateField = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        """
        Returns the string representation of the comment.
        """
        return self.id

    def save(self, *args, **kwargs) -> None:
        """
        Overrides the save method to generate a UUID for the comment ID if not already set.
        """
        if not self.id:  # Check if the ID is not set
            self.id = str(uuid.uuid4())  # Generate a unique UUID
        super().save(*args, **kwargs)  # Call the parent class's save method
