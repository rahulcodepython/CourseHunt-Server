from django.contrib.postgres.fields import ArrayField
from django.db import models
import uuid


class Course(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=120, editable=False)
    name = models.CharField(default="", max_length=120, null=True, blank=True)
    description = models.TextField(default="", null=True, blank=True)
    price = models.IntegerField(default=0)
    offer = models.IntegerField(default=0)
    duration = models.IntegerField(default=0)
    chapter = models.IntegerField(default=1)
    overview = models.TextField(default="", null=True, blank=True)
    cupon_code = models.ForeignKey(
        "CuponCode",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="course_cupon_code",
    )
    faq = models.ManyToManyField("FAQ", blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("draft", "Draft"),
            ("published", "Published"),
        ],
        default="draft",
    )
    chapters = ArrayField(
        models.CharField(max_length=120, blank=True),
        default=list,
        null=True,
        blank=True,
    )
    created_at = models.CharField(max_length=50)

    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())

        super(Course, self).save(*args, **kwargs)


class Chapter(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=120, editable=False)
    name = models.CharField(max_length=120, default="", null=True, blank=True)
    duration = models.IntegerField(default=0)
    course = models.ForeignKey(
        "Course", on_delete=models.CASCADE, related_name="chapter_course"
    )
    lessons = ArrayField(
        models.CharField(max_length=120, blank=True),
        default=list,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())

        super(Chapter, self).save(*args, **kwargs)


class Lesson(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=120, editable=False)
    name = models.CharField(max_length=120)
    videoURL = models.CharField(max_length=120, blank=True, null=True)
    notesURL = models.CharField(max_length=120, blank=True, null=True)
    presentationURL = models.CharField(max_length=120, blank=True, null=True)
    codeURL = models.CharField(max_length=120, blank=True, null=True)
    content = models.TextField(default="", null=True, blank=True)
    score = models.IntegerField(default=0)
    quizes = ArrayField(
        models.CharField(max_length=120, blank=True),
        default=list,
        null=True,
        blank=True,
    )
    chapter = models.ForeignKey("Chapter", on_delete=models.CASCADE)
    course = models.ForeignKey("Course", on_delete=models.CASCADE)

    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())

        super(Lesson, self).save(*args, **kwargs)


class Quiz(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=120, editable=False)
    question = models.CharField(max_length=120)
    answer = models.IntegerField(default=0)
    options = ArrayField(models.CharField(max_length=120, blank=True), default=list)
    lesson = models.ForeignKey("Lesson", on_delete=models.CASCADE)

    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())

        super(Quiz, self).save(*args, **kwargs)


class FAQ(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=120, editable=False)
    question = models.CharField(max_length=120)
    answer = models.TextField()

    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())

        super(FAQ, self).save(*args, **kwargs)


class CuponCode(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=120, editable=False)
    code = models.CharField(max_length=120)
    discount = models.IntegerField(default=0)
    expiry = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())

        super(CuponCode, self).save(*args, **kwargs)
