from apps.courses.models import Course, Lesson
from .models import CourseProgress, LessonProgressEvent


def update_course_progress(user, course: Course):
    total_lessons = Lesson.objects.filter(module__course=course, is_published=True).count()
    done_lessons = (
        LessonProgressEvent.objects.filter(
            user=user,
            lesson__module__course=course,
            lesson__is_published=True,
            event_type="done",
        )
        .values("lesson")
        .distinct()
        .count()
    )
    percent = 0
    if total_lessons:
        percent = round(done_lessons / total_lessons * 100, 1)
    progress, _ = CourseProgress.objects.get_or_create(user=user, course=course)
    progress.percent = percent
    progress.save()
    return progress
