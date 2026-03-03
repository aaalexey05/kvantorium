from django.db import models


class ContactInfo(models.Model):
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    map_url = models.URLField(blank=True, max_length=2048)
    schedule = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Контакты"
        verbose_name_plural = "Контакты"

    def __str__(self):
        return self.address
