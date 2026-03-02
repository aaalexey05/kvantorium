from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from .models import Course, CourseModule, Lesson, LessonBlock
from .forms import LessonForm, LessonBlockForm


@login_required
@require_POST
def create_lesson(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(CourseModule, pk=module_id, course=course)
    form = LessonForm(request.POST)
    if form.is_valid():
        lesson = form.save(commit=False)
        lesson.module = module
        lesson.save()
        return render(request, "courses/partials/module_lessons.html", {"module": module})
    return render(request, "courses/partials/lesson_form.html", {"form": form, "module": module})


@login_required
@require_POST
def add_block(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    form = LessonBlockForm(request.POST)
    if form.is_valid():
        block = form.save(commit=False)
        block.lesson = lesson
        block.save()
        return render(request, "courses/partials/lesson_blocks.html", {"lesson": lesson})
    return render(request, "courses/partials/block_form.html", {"form": form, "lesson": lesson})
