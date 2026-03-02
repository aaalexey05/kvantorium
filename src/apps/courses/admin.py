from django.contrib import admin
from .models import Course, CourseModule, Lesson, LessonBlock, Enrollment


class LessonBlockInline(admin.TabularInline):
    model = LessonBlock
    extra = 1


class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "created_by", "created_at")
    list_filter = ("status",)
    inlines = [CourseModuleInline]


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_editable = ("order",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "order", "is_published")
    list_filter = ("is_published",)
    inlines = [LessonBlockInline]


@admin.register(LessonBlock)
class LessonBlockAdmin(admin.ModelAdmin):
    list_display = ("lesson", "type", "order")
    list_editable = ("order",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "created_at")
