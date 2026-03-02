from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("name", "author_type", "rating", "is_approved", "created_at")
    list_filter = ("is_approved", "author_type")
    search_fields = ("name", "text")
    list_editable = ("is_approved",)
