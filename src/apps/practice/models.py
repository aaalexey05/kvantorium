from django.db import models
from django.conf import settings
from apps.courses.models import Lesson


class PracticeTask(models.Model):
    TASK_TYPES = (("quiz", "Тест"), ("code", "Код"), ("text", "Ответ текстом"))
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    payload = models.JSONField(default=dict)  # хранит тесты/ожидаемый вывод и т.п.
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.lesson.title}: {self.title}"


class TaskAttempt(models.Model):
    task = models.ForeignKey(PracticeTask, on_delete=models.CASCADE, related_name="attempts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="task_attempts")
    status = models.CharField(max_length=20, default="pending")
    score = models.FloatField(default=0)
    submitted_payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
