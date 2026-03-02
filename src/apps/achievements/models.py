from django.db import models


class Achievement(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    year = models.CharField(max_length=10, blank=True)
    category = models.CharField(max_length=100, blank=True)
    media = models.ImageField(upload_to="achievements/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
