from django.db import models


class Review(models.Model):
    AUTHOR_TYPES = (("parent", "Родитель"), ("student", "Ученик"), ("alumni", "Выпускник"))
    name = models.CharField(max_length=120)
    author_type = models.CharField(max_length=20, choices=AUTHOR_TYPES)
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_author_type_display()})"
