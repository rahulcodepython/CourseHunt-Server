from django.contrib.postgres.fields import ArrayField
from django.db import models
import uuid


class Course(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=120)
    name = models.CharField(max_length=120)
    description = models.TextField()
    price = models.IntegerField(default=0)
    offer = models.IntegerField(default=0)
    duration = models.IntegerField(default=0)
    chapter = models.IntegerField(default=0)
    overview = models.TextField()
    faq = models.ManyToManyField("FAQ")
    status = models.CharField(
        max_length=50, choices=[("draft", "Draft"), ("published", "Published")]
    )
    chapters = ArrayField(models.CharField(max_length=120, blank=True), default=list)
    created_at = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = uuid.uuid5()

        super(Course, self).save(*args, **kwargs)


class Chapter(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=120)
    name = models.CharField(max_length=120)
    duration = models.IntegerField(default=0)
    course = models.ForeignKey(
        "Course", on_delete=models.CASCADE, related_name="chapter_course"
    )
    lessons = ArrayField(models.CharField(max_length=120, blank=True), default=list)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = uuid.uuid5()

        super(Chapter, self).save(*args, **kwargs)


class Lesson(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=120)
    name = models.CharField(max_length=120)
    videoURL = models.CharField(max_length=120)
    notesURL = models.CharField(max_length=120)
    presentationURL = models.CharField(max_length=120)
    codeURL = models.CharField(max_length=120)
    content = models.TextField()
    score = models.IntegerField(default=0)
    quizes = ArrayField(models.CharField(max_length=120, blank=True), default=list)
    chapter = models.ForeignKey("Chapter", on_delete=models.CASCADE)
    course = models.ForeignKey("Course", on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = uuid.uuid5()

        super(Lesson, self).save(*args, **kwargs)


class Quiz(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=120)
    question = models.CharField(max_length=120)
    answer = models.IntegerField(default=0)
    options = ArrayField(models.CharField(max_length=120, blank=True), default=list)
    lesson = models.ForeignKey("Lesson", on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = uuid.uuid5()

        super(Quiz, self).save(*args, **kwargs)


class FAQ(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=120)
    question = models.CharField(max_length=120)
    answer = models.TextField()

    def __str__(self):
        return self.question

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = uuid.uuid4()

        super(FAQ, self).save(*args, **kwargs)
