from django.contrib.auth import get_user_model
from django.db import models
from authentication.models import Instructor

User = get_user_model()

LEVEL =(
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
)

class Course(models.Model):
    id = models.CharField(max_length=255, primary_key=True, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True)
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True)
    is_published = models.BooleanField(default=False)
    instructor = models.ForeignKey(
        Instructor, on_delete=models.SET_NULL, related_name='instructed_courses', blank=True, null=True)
    modules = models.ManyToManyField(
        'Module', related_name='courses', blank=True)
    image = models.URLField(blank=True, null=True)
    badge = models.CharField(max_length=255, blank=True, null=True)
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00)
    rating_count = models.PositiveIntegerField(default=0)
    total_students = models.PositiveIntegerField(default=0)
    total_hours_of_content = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00)
    total_lectures = models.PositiveIntegerField(default=0)
    language = models.CharField(max_length=255, blank=True, null=True)
    level = models.CharField(max_length=255, blank=True, null=True, choices=LEVEL)
    category = models.CharField(max_length=255, blank=True, null=True)
    subtitles = models.BooleanField(default=False)
    keywords = models.CharField(max_length=255, blank=True, null=True)
    intro_video = models.URLField(blank=True, null=True)
    faq = models.ManyToManyField("FAQ", related_name='courses_faq', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Module(models.Model):
    id = models.CharField(max_length=255, primary_key=True, unique=True)
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    lecture_duration = models.IntegerField(default=0)
    lectures = models.ManyToManyField(
        'Lecture', related_name='modules', blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

LECTURE_TYPE = (
    ('video', 'Video'),
    ('document', 'Document'),
)

class Lecture(models.Model):
    id = models.CharField(max_length=255, primary_key=True, unique=True)
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    video_url = models.URLField(blank=True, null=True)
    pdf_url = models.URLField(blank=True, null=True)
    document_url = models.URLField(blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)
    duration = models.IntegerField(default=0)
    type = models.CharField(
        max_length=255, choices=LECTURE_TYPE, default='video'
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class UserCourse(models.Model):
    id = models.CharField(max_length=255, primary_key=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    is_completed = models.BooleanField(default=False)
    is_certified = models.BooleanField(default=False)

    last_completed_lecture = models.ForeignKey(
        Lecture, on_delete=models.SET_NULL, null=True, blank=True, related_name='last_done_by_users'
    )
    completed_lectures = models.ManyToManyField(
        Lecture, related_name='completed_by_users', blank=True)

    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

class FAQ(models.Model):
    id = models.CharField(max_length=255, primary_key=True, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="faqs_course")
    question = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return self.id