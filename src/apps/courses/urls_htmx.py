from django.urls import path
from . import htmx_views

app_name = "courses_htmx"

urlpatterns = [
    path('<slug:course_slug>/modules/<int:module_id>/lessons/new/', htmx_views.create_lesson, name='lesson_create'),
    path('lesson/<int:lesson_id>/blocks/new/', htmx_views.add_block, name='block_create'),
]
