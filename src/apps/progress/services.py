from apps.courses.models import Course
from .models import CourseProgress, LessonProgressEvent


def update_course_progress(user, course: Course):
    total_lessons = course.modules.prefetch_related("lessons").aggregate(count=models.Count("lessons"))["count"] or 0
    done_lessons = (
        LessonProgressEvent.objects.filter(user=user, lesson__module__course=course)
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
