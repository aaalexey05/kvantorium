from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.achievements.models import Achievement
from apps.courses.models import Course, CourseModule, Enrollment, Lesson, LessonBlock
from apps.news.models import NewsPost
from apps.reviews.models import Review


class Command(BaseCommand):
    help = "Seed demo users and content for Kvantorium LMS"

    def handle(self, *args, **options):
        user_model = get_user_model()

        admin, _ = user_model.objects.get_or_create(
            email="admin@kvantorium.local",
            defaults={"is_staff": True, "is_superuser": True, "role": user_model.Role.ADMIN},
        )
        admin.role = user_model.Role.ADMIN
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password("Kv@123456")
        admin.save()

        teacher, _ = user_model.objects.get_or_create(
            email="teacher@kvantorium.local",
            defaults={"is_staff": True, "role": user_model.Role.TEACHER},
        )
        teacher.role = user_model.Role.TEACHER
        teacher.is_staff = True
        teacher.set_password("Kv@123456")
        teacher.save()

        student, _ = user_model.objects.get_or_create(
            email="student@kvantorium.local",
            defaults={"role": user_model.Role.STUDENT},
        )
        student.role = user_model.Role.STUDENT
        student.set_password("Kv@123456")
        student.save()

        parent, _ = user_model.objects.get_or_create(
            email="parent@kvantorium.local",
            defaults={"role": user_model.Role.PARENT},
        )
        parent.role = user_model.Role.PARENT
        parent.set_password("Kv@123456")
        parent.save()

        python_course, _ = Course.objects.get_or_create(
            title="Python для начинающих",
            defaults={
                "short_description": "Введение в программирование: переменные, условия, циклы и функции.",
                "description": "Практический курс с мини-проектами и простыми заданиями на каждом уроке.",
                "tags": "Python, Начинающий",
                "status": "published",
                "created_by": teacher,
            },
        )

        module_basics, _ = CourseModule.objects.get_or_create(
            course=python_course,
            title="Базовый синтаксис",
            order=1,
        )
        lesson_first, _ = Lesson.objects.get_or_create(
            module=module_basics,
            title="Первая программа",
            order=1,
            is_published=True,
            defaults={"summary": "Знакомимся с print и правилами записи кода."},
        )
        lesson_first.summary = "Знакомимся с print и правилами записи кода."
        lesson_first.save(update_fields=["summary"])

        LessonBlock.objects.get_or_create(
            lesson=lesson_first,
            order=1,
            type="text",
            payload={"text": "<p>Сегодня напишем первую программу и увидим, как работает интерпретатор Python.</p>"},
        )
        LessonBlock.objects.get_or_create(
            lesson=lesson_first,
            order=2,
            type="code",
            language="python",
            payload={"code": "print('Hello, Kvantorium!')"},
        )

        scratch_course, _ = Course.objects.get_or_create(
            title="Scratch: первые игры",
            defaults={
                "short_description": "Создаем игры и анимации в визуальной среде Scratch.",
                "description": "Курс для младших школьников с акцентом на логику и творчество.",
                "tags": "Scratch, Junior",
                "status": "published",
                "created_by": teacher,
            },
        )
        scratch_module, _ = CourseModule.objects.get_or_create(
            course=scratch_course,
            title="Знакомство со спрайтами",
            order=1,
        )
        scratch_lesson, _ = Lesson.objects.get_or_create(
            module=scratch_module,
            title="Двигаем героя по сцене",
            order=1,
            is_published=True,
            defaults={"summary": "Соберем первую интерактивную сцену."},
        )
        LessonBlock.objects.get_or_create(
            lesson=scratch_lesson,
            order=1,
            type="text",
            payload={"text": "<p>Добавим спрайт, фон и простые команды движения по нажатию клавиш.</p>"},
        )

        Enrollment.objects.get_or_create(user=student, course=python_course)
        Enrollment.objects.get_or_create(user=student, course=scratch_course)

        NewsPost.objects.get_or_create(
            title="Старт новой программы Python",
            slug="start-python",
            defaults={
                "summary": "Открыт новый поток курса Python для начинающих.",
                "body": "<p>Программа рассчитана на 8 недель, с домашними заданиями и мини-проектом.</p>",
                "published_at": timezone.now(),
                "status": "published",
            },
        )
        NewsPost.objects.get_or_create(
            title="Открыт набор в Scratch-группу",
            slug="scratch-group-open",
            defaults={
                "summary": "Новая группа для детей 8-11 лет начинает обучение в этом месяце.",
                "body": "<p>Записывайтесь на курс, чтобы создать первую игру и показать ее на демо-дне.</p>",
                "published_at": timezone.now(),
                "status": "published",
            },
        )

        Achievement.objects.get_or_create(
            title="Победа на региональном хакатоне",
            defaults={
                "description": "Команда Кванториума взяла 1 место в номинации 'Образовательный продукт'.",
                "year": "2025",
                "category": "Хакатоны",
            },
        )
        Achievement.objects.get_or_create(
            title="Приз зрительских симпатий",
            defaults={
                "description": "Проект учеников по робототехнике получил спецприз жюри.",
                "year": "2024",
                "category": "Робототехника",
            },
        )

        Review.objects.get_or_create(
            name="Алексей",
            author_type="parent",
            rating=5,
            text="Ребенок в восторге от занятий и начал сам писать маленькие программы.",
            defaults={"is_approved": True},
        )
        Review.objects.get_or_create(
            name="Ирина",
            author_type="student",
            rating=5,
            text="Очень понравились уроки и формат с практикой после каждой темы.",
            defaults={"is_approved": True},
        )

        self.stdout.write(self.style.SUCCESS("Demo data seeded: users, courses, news, achievements, reviews."))
