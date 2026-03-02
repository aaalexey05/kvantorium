from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Course(models.Model):
    STATUS_CHOICES = (("draft", "Черновик"), ("published", "Опубликован"))
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    short_description = models.TextField()
    description = models.TextField(blank=True)
    age_group = models.CharField(max_length=50, blank=True)
    level = models.CharField(max_length=50, blank=True)
    tags = models.CharField(max_length=200, blank=True)
    cover = models.ImageField(upload_to="covers/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="courses")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class CourseModule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} / {self.title}"


class Lesson(models.Model):
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


class LessonBlock(models.Model):
    BLOCK_TYPES = (
        ("text", "Текст"),
        ("image", "Изображение"),
        ("code", "Код"),
        ("video", "Видео"),
        ("file", "Файл"),
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="blocks")
    type = models.CharField(max_length=20, choices=BLOCK_TYPES)
    order = models.PositiveIntegerField(default=0)
    payload = models.JSONField(default=dict)
    language = models.CharField(max_length=30, blank=True)  # для code блока

    class Meta:
        ordering = ["order"]


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user.email} -> {self.course.title}"
