from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from apps.courses.models import Lesson
from .models import LessonProgressEvent
from .services import update_course_progress


@login_required
@require_POST
def mark_lesson_read(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    LessonProgressEvent.objects.get_or_create(user=request.user, lesson=lesson, event_type="done")
    progress_record = update_course_progress(request.user, lesson.module.course)
    if request.headers.get("HX-Request"):
        return render(
            request,
            "courses/partials/progress_badge.html",
            {"progress_record": progress_record},
        )
    return render(
        request,
        "courses/lesson_detail.html",
        {"lesson": lesson, "course": lesson.module.course, "progress_record": progress_record},
    )
