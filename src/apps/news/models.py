from django.db import models


class NewsPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    summary = models.TextField()
    body = models.TextField()
    published_at = models.DateTimeField()
    status = models.CharField(max_length=20, default="published")
    image = models.ImageField(upload_to="news/", blank=True, null=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title
