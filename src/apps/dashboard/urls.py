from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.role_dashboard, name="home"),
    path("admin/", views.admin_dashboard, name="admin_home"),
    path("admin/courses/", views.admin_courses, name="admin_courses"),
    path("admin/courses/<int:pk>/edit/", views.admin_course_edit, name="admin_course_edit"),
    path("admin/courses/<int:pk>/delete/", views.admin_course_delete, name="admin_course_delete"),
    path("admin/users/", views.admin_users, name="admin_users"),
    path("admin/users/<int:pk>/edit/", views.admin_user_edit, name="admin_user_edit"),
    path("admin/news/", views.admin_news, name="admin_news"),
    path("admin/news/<int:pk>/delete/", views.admin_news_delete, name="admin_news_delete"),
    path("admin/achievements/", views.admin_achievements, name="admin_achievements"),
    path(
        "admin/achievements/<int:pk>/delete/",
        views.admin_achievements_delete,
        name="admin_achievements_delete",
    ),
    path("teacher/", views.teacher_dashboard, name="teacher_home"),
    path("teacher/courses/", views.teacher_courses, name="teacher_courses"),
    path("teacher/courses/create/", views.teacher_course_create, name="teacher_course_create"),
    path("teacher/courses/<int:pk>/edit/", views.teacher_course_edit, name="teacher_course_edit"),
    path("teacher/courses/<int:pk>/autosave/", views.teacher_course_autosave, name="teacher_course_autosave"),
    path("teacher/courses/<int:pk>/delete/", views.teacher_course_delete, name="teacher_course_delete"),
    path("teacher/courses/<int:pk>/modules/add/", views.teacher_course_add_module, name="teacher_course_add_module"),
    path("teacher/courses/<int:pk>/lessons/add/", views.teacher_course_add_lesson, name="teacher_course_add_lesson"),
    path("teacher/courses/<int:pk>/blocks/add/", views.teacher_course_add_block, name="teacher_course_add_block"),
    path(
        "teacher/courses/<int:pk>/lessons/<int:lesson_id>/blocks/reorder/",
        views.teacher_course_reorder_blocks,
        name="teacher_course_reorder_blocks",
    ),
    path(
        "teacher/courses/<int:pk>/blocks/<int:block_id>/duplicate/",
        views.teacher_course_duplicate_block,
        name="teacher_course_duplicate_block",
    ),
    path("teacher/lessons/<int:lesson_id>/preview/", views.teacher_lesson_preview, name="teacher_lesson_preview"),
    path("teacher/stats/", views.teacher_stats, name="teacher_stats"),
]
