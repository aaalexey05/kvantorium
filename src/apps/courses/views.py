from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import Course, Lesson, Enrollment
from apps.progress.models import CourseProgress
from apps.progress.services import update_course_progress


def course_list(request):
    courses = Course.objects.filter(status="published").select_related("created_by")
    return render(request, "courses/course_list.html", {"courses": courses})


def course_detail(request, slug):
    course = get_object_or_404(Course.objects.prefetch_related("modules__lessons__blocks"), slug=slug)
    can_view_draft = (
        request.user.is_authenticated
        and (
            request.user.role == "admin"
            or course.created_by_id == request.user.id
            or request.user.is_superuser
        )
    )
    if course.status != "published" and not can_view_draft:
        raise Http404("Курс не опубликован")
    enrolled = False
    course_progress = None
    if request.user.is_authenticated:
        enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
        course_progress = CourseProgress.objects.filter(user=request.user, course=course).first()
    return render(
        request,
        "courses/course_detail.html",
        {"course": course, "enrolled": enrolled, "course_progress": course_progress},
    )


def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson.objects.prefetch_related("blocks", "module__course"), pk=pk)
    course = lesson.module.course
    can_view_unpublished_lesson = (
        request.user.is_authenticated
        and (
            request.user.role == "admin"
            or course.created_by_id == request.user.id
            or request.user.is_superuser
        )
    )
    if lesson.is_published is False and not can_view_unpublished_lesson:
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
        CourseProgress.objects.filter(user=request.user, course=course).delete()
        enrolled = False
    else:
        update_course_progress(request.user, course)
        enrolled = True
    if request.headers.get("HX-Request"):
        return render(request, "courses/partials/enroll_button.html", {"course": course, "enrolled": enrolled})
    return redirect("courses:detail", slug=slug)
