from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import Course, CourseModule, Lesson, LessonBlock, Enrollment
from apps.progress.models import CourseProgress


def course_list(request):
    courses = Course.objects.filter(status="published").select_related("created_by")
    return render(request, "courses/course_list.html", {"courses": courses})


def course_detail(request, slug):
    course = get_object_or_404(
        Course.objects.prefetch_related("modules__lessons__blocks"), slug=slug, status="published"
    )
    enrolled = False
    if request.user.is_authenticated:
        enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    return render(request, "courses/course_detail.html", {"course": course, "enrolled": enrolled})


def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson.objects.prefetch_related("blocks", "module__course"), pk=pk)
    course = lesson.module.course
    if lesson.is_published is False and not request.user.is_staff:
        return HttpResponseBadRequest("Урок еще не опубликован")
    progress_record = None
    if request.user.is_authenticated:
        progress_record = CourseProgress.objects.filter(user=request.user, course=course).first()
    return render(
        request,
        "courses/lesson_detail.html",
        {"lesson": lesson, "course": course, "progress_record": progress_record},
    )


@login_required
@require_POST
def enroll_toggle(request, slug):
    course = get_object_or_404(Course, slug=slug)
    enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    if not created:
        enrollment.delete()
        enrolled = False
    else:
        enrolled = True
    if request.headers.get("HX-Request"):
        return render(request, "courses/partials/enroll_button.html", {"course": course, "enrolled": enrolled})
    return redirect("courses:detail", slug=slug)
