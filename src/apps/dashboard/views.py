from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Avg, Count, Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from urllib.parse import parse_qs, urlparse

from apps.achievements.models import Achievement
from apps.accounts.permissions import admin_required, teacher_or_admin_required
from apps.core.map_utils import build_contact_map_context
from apps.core.models import ContactInfo
from apps.courses.models import Course, CourseModule, Lesson, LessonBlock
from apps.news.models import NewsPost
from apps.reviews.models import Review

from .forms import (
    AdminAchievementForm,
    AdminContactForm,
    AdminCourseForm,
    AdminNewsForm,
    AdminUserForm,
    TeacherCourseForm,
    TeacherCourseStructureForm,
    TeacherLessonBlockForm,
    TeacherLessonForm,
    TeacherModuleForm,
)


User = get_user_model()


def _parse_lines(value: str):
    return [line.strip() for line in value.splitlines() if line.strip()]


def _is_owner_or_admin(user, course: Course):
    return user.role == User.Role.ADMIN or course.created_by_id == user.id


def _apply_structure(course: Course, structure_form: TeacherCourseStructureForm):
    module_titles = _parse_lines(structure_form.cleaned_data.get("module_titles", ""))
    lesson_titles = _parse_lines(structure_form.cleaned_data.get("lesson_titles", ""))

    if module_titles:
        current_max = course.modules.aggregate(max_order=Max("order"))["max_order"] or 0
        for offset, title in enumerate(module_titles, start=1):
            CourseModule.objects.get_or_create(
                course=course,
                title=title,
                defaults={"order": current_max + offset},
            )

    first_module = course.modules.order_by("order", "id").first()
    if not first_module:
        first_module = CourseModule.objects.create(course=course, title="Введение", order=1)

    if lesson_titles:
        lesson_max_order = first_module.lessons.aggregate(max_order=Max("order"))["max_order"] or 0
        for offset, title in enumerate(lesson_titles, start=1):
            Lesson.objects.get_or_create(
                module=first_module,
                title=title,
                defaults={
                    "summary": "Краткое описание урока будет добавлено позже.",
                    "order": lesson_max_order + offset,
                    "is_published": True,
                },
            )


def _build_block_payload(form: TeacherLessonBlockForm):
    block_type = form.cleaned_data["type"]
    text_content = form.cleaned_data.get("text_content", "")
    resource_url = form.cleaned_data.get("resource_url", "")
    caption = form.cleaned_data.get("caption", "")
    language = form.cleaned_data.get("language", "")

    if block_type == "text":
        return {"text": text_content}, ""
    if block_type == "code":
        return {"code": text_content}, language
    if block_type == "image":
        return {"url": resource_url, "caption": caption}, ""
    if block_type == "video":
        return {"url": resource_url}, ""
    if block_type == "file":
        return {"url": resource_url}, ""
    return {}, ""


def _normalize_video_url(url: str):
    raw = (url or "").strip()
    if not raw:
        return raw
    parsed = urlparse(raw)
    host = parsed.netloc.lower()
    path = parsed.path
    if "youtube.com" in host:
        query = parse_qs(parsed.query or "")
        video_id = query.get("v", [None])[0]
        if not video_id and "/shorts/" in path:
            video_id = path.rstrip("/").split("/")[-1]
        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
    if "youtu.be" in host:
        video_id = path.strip("/")
        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
    return raw


def _apply_lesson_template(lesson: Lesson, template_key: str):
    templates = {
        "theory_code_task": [
            {
                "type": "text",
                "payload": {
                    "text": "<h3>Теория</h3><p>Кратко объясните тему урока простыми словами.</p>",
                },
                "language": "",
            },
            {
                "type": "code",
                "payload": {"code": "print('Пример кода')"},
                "language": "python",
            },
            {
                "type": "text",
                "payload": {
                    "text": "<h3>Задание</h3><ul><li>Сделайте шаг 1</li><li>Сделайте шаг 2</li></ul>",
                },
                "language": "",
            },
        ],
        "theory_only": [
            {
                "type": "text",
                "payload": {"text": "<h3>Теория</h3><p>Основной материал урока.</p>"},
                "language": "",
            }
        ],
        "practice_only": [
            {
                "type": "text",
                "payload": {"text": "<h3>Практика</h3><p>Описание практического задания.</p>"},
                "language": "",
            },
            {
                "type": "code",
                "payload": {"code": "# Решение задания\n"},
                "language": "python",
            },
        ],
    }
    blocks = templates.get(template_key, [])
    if not blocks:
        return
    for index, block in enumerate(blocks, start=1):
        lesson.blocks.create(
            type=block["type"],
            order=index,
            payload=block["payload"],
            language=block.get("language", ""),
        )


@login_required
def role_dashboard(request):
    if request.user.role == User.Role.ADMIN:
        return redirect("dashboard:admin_home")
    if request.user.role == User.Role.TEACHER:
        return redirect("dashboard:teacher_home")
    return redirect("accounts:profile")


@login_required
@admin_required
def admin_dashboard(request):
    total_courses = Course.objects.count()
    published_courses = Course.objects.filter(status="published").count()
    total_lessons = Lesson.objects.count()
    published_lessons = Lesson.objects.filter(is_published=True).count()
    user_counts = User.objects.values("role").annotate(total=Count("id"))
    counts = {item["role"]: item["total"] for item in user_counts}
    return render(
        request,
        "dashboard/admin_dashboard.html",
        {
            "total_courses": total_courses,
            "published_courses": published_courses,
            "total_lessons": total_lessons,
            "published_lessons": published_lessons,
            "students_count": counts.get(User.Role.STUDENT, 0),
            "teachers_count": counts.get(User.Role.TEACHER, 0),
            "parents_count": counts.get(User.Role.PARENT, 0),
            "news_count": NewsPost.objects.count(),
            "achievements_count": Achievement.objects.count(),
            "contacts_count": ContactInfo.objects.count(),
        },
    )


@login_required
@admin_required
def admin_courses(request):
    courses = (
        Course.objects.select_related("created_by")
        .annotate(students_count=Count("enrollments", distinct=True))
        .order_by("-created_at")
    )
    return render(request, "dashboard/admin_courses.html", {"courses": courses})


@login_required
@admin_required
def admin_course_edit(request, pk):
    course = get_object_or_404(Course.objects.select_related("created_by"), pk=pk)
    if request.method == "POST":
        form = AdminCourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Курс обновлен.")
            return redirect("dashboard:admin_courses")
    else:
        form = AdminCourseForm(instance=course)
    return render(request, "dashboard/admin_course_edit.html", {"form": form, "course": course})


@login_required
@admin_required
@require_POST
def admin_course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    course.delete()
    messages.success(request, "Курс удален.")
    return redirect("dashboard:admin_courses")


@login_required
@admin_required
def admin_users(request):
    role_filter = request.GET.get("role", "")
    users = User.objects.all().order_by("email")
    if role_filter:
        users = users.filter(role=role_filter)
    return render(
        request,
        "dashboard/admin_users.html",
        {
            "users": users,
            "role_filter": role_filter,
            "role_choices": User.Role.choices,
        },
    )


@login_required
@admin_required
def admin_user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = AdminUserForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)
            if updated_user.role == User.Role.ADMIN:
                updated_user.is_staff = True
            elif updated_user.role == User.Role.TEACHER:
                updated_user.is_staff = True
            else:
                updated_user.is_staff = False
            updated_user.save()
            messages.success(request, "Пользователь обновлен.")
            return redirect("dashboard:admin_users")
    else:
        form = AdminUserForm(instance=user)
    return render(request, "dashboard/admin_user_edit.html", {"form": form, "target_user": user})


@login_required
@admin_required
def admin_news(request):
    if request.method == "POST":
        form = AdminNewsForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.published_at = timezone.now()
            post.save()
            messages.success(request, "Новость добавлена.")
            return redirect("dashboard:admin_news")
    else:
        form = AdminNewsForm()

    posts = NewsPost.objects.all().order_by("-published_at")[:20]
    return render(request, "dashboard/admin_news.html", {"form": form, "posts": posts})


@login_required
@admin_required
@require_POST
def admin_news_delete(request, pk):
    post = get_object_or_404(NewsPost, pk=pk)
    post.delete()
    messages.success(request, "Новость удалена.")
    return redirect("dashboard:admin_news")


@login_required
@admin_required
def admin_achievements(request):
    if request.method == "POST":
        form = AdminAchievementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Достижение добавлено.")
            return redirect("dashboard:admin_achievements")
    else:
        form = AdminAchievementForm()

    items = Achievement.objects.all().order_by("-created_at")[:20]
    return render(request, "dashboard/admin_achievements.html", {"form": form, "items": items})


@login_required
@admin_required
@require_POST
def admin_achievements_delete(request, pk):
    item = get_object_or_404(Achievement, pk=pk)
    item.delete()
    messages.success(request, "Достижение удалено.")
    return redirect("dashboard:admin_achievements")


@login_required
@admin_required
def admin_contacts(request):
    info = ContactInfo.objects.order_by("id").first()
    if info is None:
        info = ContactInfo.objects.create(address="г. Барнаул, ул. Пример, 10")

    if request.method == "POST":
        form = AdminContactForm(request.POST, instance=info)
        if form.is_valid():
            form.save()
            messages.success(request, "Контакты обновлены.")
            return redirect("dashboard:admin_contacts")
    else:
        form = AdminContactForm(instance=info)

    map_preview_attrs = {
        "hx-get": reverse("dashboard:admin_contacts_map_preview"),
        "hx-trigger": "input changed delay:700ms, blur",
        "hx-target": "#contact-map-preview",
        "hx-swap": "innerHTML",
        "hx-include": "[name='city'],[name='street'],[name='house'],[name='map_url']",
    }
    form.fields["city"].widget.attrs.update(map_preview_attrs)
    form.fields["street"].widget.attrs.update(map_preview_attrs)
    form.fields["house"].widget.attrs.update(map_preview_attrs)
    form.fields["map_url"].widget.attrs.update(map_preview_attrs)

    if form.is_bound:
        preview_address = AdminContactForm.compose_address(
            form.data.get("city", ""),
            form.data.get("street", ""),
            form.data.get("house", ""),
        )
        preview_map_url = form.data.get("map_url", "")
    else:
        preview_address = AdminContactForm.compose_address(
            form.fields["city"].initial or "",
            form.fields["street"].initial or "",
            form.fields["house"].initial or "",
        )
        preview_map_url = info.map_url
    map_ctx = build_contact_map_context(preview_address, preview_map_url)
    return render(
        request,
        "dashboard/admin_contacts.html",
        {
            "form": form,
            "info": info,
            "preview_address": preview_address,
            **map_ctx,
        },
    )


@login_required
@admin_required
def admin_contacts_map_preview(request):
    address = AdminContactForm.compose_address(
        request.GET.get("city", ""),
        request.GET.get("street", ""),
        request.GET.get("house", ""),
    )
    map_url = request.GET.get("map_url", "")
    map_ctx = build_contact_map_context(address, map_url)
    return render(
        request,
        "dashboard/partials/contact_map_preview.html",
        {
            "address": address,
            **map_ctx,
        },
    )


@login_required
@teacher_or_admin_required
def teacher_dashboard(request):
    if request.user.role == User.Role.ADMIN:
        return redirect("dashboard:admin_home")

    courses = (
        Course.objects.filter(created_by=request.user)
        .annotate(
            students_count=Count("enrollments", distinct=True),
            avg_progress=Avg("progress_records__percent"),
        )
        .order_by("-created_at")
    )
    latest_reviews = Review.objects.filter(is_approved=True).order_by("-created_at")[:5]
    return render(
        request,
        "dashboard/teacher_dashboard.html",
        {"courses": courses, "latest_reviews": latest_reviews},
    )


@login_required
@teacher_or_admin_required
def teacher_courses(request):
    if request.user.role == User.Role.ADMIN:
        courses = (
            Course.objects.select_related("created_by")
            .annotate(students_count=Count("enrollments", distinct=True))
            .order_by("-created_at")
        )
    else:
        courses = (
            Course.objects.filter(created_by=request.user)
            .annotate(students_count=Count("enrollments", distinct=True))
            .order_by("-created_at")
        )
    return render(request, "dashboard/teacher_courses.html", {"courses": courses})


@login_required
@teacher_or_admin_required
def teacher_course_create(request):
    if request.method == "POST":
        form = TeacherCourseForm(request.POST, request.FILES)
        structure_form = TeacherCourseStructureForm(request.POST)
        if form.is_valid() and structure_form.is_valid():
            course = form.save(commit=False)
            course.created_by = request.user
            course.save()
            _apply_structure(course, structure_form)
            messages.success(request, "Курс сохранен. Заполните содержимое ниже.")
            return redirect("dashboard:teacher_course_edit", pk=course.pk)
    else:
        form = TeacherCourseForm()
        structure_form = TeacherCourseStructureForm()
    return render(
        request,
        "dashboard/teacher_course_form.html",
        {
            "form": form,
            "structure_form": structure_form,
            "page_title": "Создать курс",
            "submit_text": "Сохранить курс",
        },
    )


@login_required
@teacher_or_admin_required
def teacher_course_edit(request, pk):
    course = get_object_or_404(Course.objects.prefetch_related("modules__lessons__blocks"), pk=pk)
    if not _is_owner_or_admin(request.user, course):
        raise PermissionDenied

    if request.method == "POST":
        form = TeacherCourseForm(request.POST, request.FILES, instance=course)
        structure_form = TeacherCourseStructureForm(request.POST)
        if form.is_valid() and structure_form.is_valid():
            form.save()
            _apply_structure(course, structure_form)
            messages.success(request, "Курс обновлен.")
            return redirect("dashboard:teacher_course_edit", pk=course.pk)
    else:
        form = TeacherCourseForm(instance=course)
        structure_form = TeacherCourseStructureForm()
    return render(
        request,
        "dashboard/teacher_course_form.html",
        {
            "form": form,
            "structure_form": structure_form,
            "page_title": "Редактировать курс",
            "submit_text": "Сохранить изменения",
            "course": course,
            "module_form": TeacherModuleForm(initial={"order": (course.modules.aggregate(max_order=Max("order"))["max_order"] or 0) + 1}),
            "lesson_form": TeacherLessonForm(initial={"order": 1, "is_published": True}),
            "block_form": TeacherLessonBlockForm(initial={"order": 1, "type": "text"}),
        },
    )


@login_required
@teacher_or_admin_required
@require_POST
def teacher_course_autosave(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if not _is_owner_or_admin(request.user, course):
        raise PermissionDenied

    form = TeacherCourseForm(request.POST, request.FILES, instance=course)
    if form.is_valid():
        form.save()
        return JsonResponse({"ok": True, "saved_at": timezone.localtime().strftime("%H:%M:%S")})
    return JsonResponse({"ok": False, "errors": form.errors}, status=400)


@login_required
@teacher_or_admin_required
@require_POST
def teacher_course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if not _is_owner_or_admin(request.user, course):
        raise PermissionDenied
    course.delete()
    messages.success(request, "Курс удален.")
    return redirect("dashboard:teacher_courses")


@login_required
@teacher_or_admin_required
@require_POST
def teacher_course_add_module(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if not _is_owner_or_admin(request.user, course):
        raise PermissionDenied

    form = TeacherModuleForm(request.POST)
    if form.is_valid():
        module = form.save(commit=False)
        module.course = course
        module.save()
        messages.success(request, "Модуль добавлен.")
    else:
        messages.error(request, "Не удалось добавить модуль.")
    return redirect("dashboard:teacher_course_edit", pk=course.pk)


@login_required
@teacher_or_admin_required
@require_POST
def teacher_course_add_lesson(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if not _is_owner_or_admin(request.user, course):
        raise PermissionDenied

    module = get_object_or_404(CourseModule, pk=request.POST.get("module_id"), course=course)
    form = TeacherLessonForm(request.POST)
    if form.is_valid():
        lesson = form.save(commit=False)
        lesson.module = module
        lesson.save()
        template_key = (request.POST.get("lesson_template") or "").strip()
        _apply_lesson_template(lesson, template_key)
        messages.success(request, "Урок добавлен.")
    else:
        messages.error(request, "Не удалось добавить урок.")
    return redirect("dashboard:teacher_course_edit", pk=course.pk)


@login_required
@teacher_or_admin_required
@require_POST
def teacher_course_add_block(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if not _is_owner_or_admin(request.user, course):
        raise PermissionDenied

    lesson = get_object_or_404(Lesson, pk=request.POST.get("lesson_id"), module__course=course)
    form = TeacherLessonBlockForm(request.POST)
    if form.is_valid():
        order = form.cleaned_data.get("order") or ((lesson.blocks.aggregate(max_order=Max("order"))["max_order"] or 0) + 1)
        payload, language = _build_block_payload(form)
        if form.cleaned_data["type"] == "video":
            payload["url"] = _normalize_video_url(payload.get("url", ""))
        lesson.blocks.create(
            type=form.cleaned_data["type"],
            order=order,
            payload=payload,
            language=language,
        )
        messages.success(request, "Блок добавлен.")
    else:
        messages.error(request, "Не удалось добавить блок.")
    return redirect("dashboard:teacher_course_edit", pk=course.pk)


@login_required
@teacher_or_admin_required
def teacher_stats(request):
    if request.user.role == User.Role.ADMIN:
        courses = Course.objects.all()
    else:
        courses = Course.objects.filter(created_by=request.user)

    courses = courses.annotate(
        students_count=Count("enrollments", distinct=True),
        avg_progress=Avg("progress_records__percent"),
    ).order_by("-created_at")

    latest_reviews = Review.objects.filter(is_approved=True).order_by("-created_at")[:8]
    return render(
        request,
        "dashboard/teacher_stats.html",
        {
            "courses": courses,
            "latest_reviews": latest_reviews,
        },
    )


@login_required
@teacher_or_admin_required
@require_POST
def teacher_course_duplicate_block(request, pk, block_id):
    course = get_object_or_404(Course, pk=pk)
    if not _is_owner_or_admin(request.user, course):
        raise PermissionDenied

    block = get_object_or_404(LessonBlock, pk=block_id, lesson__module__course=course)
    max_order = block.lesson.blocks.aggregate(max_order=Max("order"))["max_order"] or 0
    block.lesson.blocks.create(
        type=block.type,
        order=max_order + 1,
        payload=block.payload,
        language=block.language,
    )
    messages.success(request, "Блок продублирован.")
    return redirect("dashboard:teacher_course_edit", pk=course.pk)


@login_required
@teacher_or_admin_required
@require_POST
def teacher_course_reorder_blocks(request, pk, lesson_id):
    course = get_object_or_404(Course, pk=pk)
    if not _is_owner_or_admin(request.user, course):
        raise PermissionDenied
    lesson = get_object_or_404(Lesson, pk=lesson_id, module__course=course)

    block_ids_raw = request.POST.get("block_ids", "")
    try:
        block_ids = [int(item) for item in block_ids_raw.split(",") if item.strip()]
    except ValueError:
        return JsonResponse({"ok": False, "error": "invalid ids"}, status=400)

    existing_ids = set(lesson.blocks.values_list("id", flat=True))
    if set(block_ids) != existing_ids:
        return JsonResponse({"ok": False, "error": "ids mismatch"}, status=400)

    with transaction.atomic():
        for order, block_id in enumerate(block_ids, start=1):
            LessonBlock.objects.filter(id=block_id, lesson=lesson).update(order=order)

    return JsonResponse({"ok": True})


@login_required
@teacher_or_admin_required
def teacher_lesson_preview(request, lesson_id):
    lesson = get_object_or_404(Lesson.objects.select_related("module__course").prefetch_related("blocks"), pk=lesson_id)
    course = lesson.module.course
    if not _is_owner_or_admin(request.user, course):
        raise PermissionDenied
    return render(request, "dashboard/lesson_preview.html", {"lesson": lesson, "course": course})
