from django.urls import path
from . import views

app_name = "progress"

urlpatterns = [
    path("lesson/<int:pk>/mark/", views.mark_lesson_read, name="mark_lesson"),
]
