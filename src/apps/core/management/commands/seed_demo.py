from datetime import timedelta
from textwrap import dedent

from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.achievements.models import Achievement
from apps.core.models import ContactInfo
from apps.courses.models import Course, CourseModule, Enrollment, Lesson, LessonBlock
from apps.news.models import NewsPost
from apps.progress.models import LessonProgressEvent
from apps.progress.services import update_course_progress
from apps.reviews.models import Review


def _txt(value: str) -> str:
    return dedent(value).strip()


class Command(BaseCommand):
    help = "Seed demo users and rich LMS data."

    def handle(self, *args, **options):
        user_model = get_user_model()

        admin_group, _ = Group.objects.get_or_create(name="Administrators")
        teacher_group, _ = Group.objects.get_or_create(name="Teachers")
        student_group, _ = Group.objects.get_or_create(name="Students")
        parent_group, _ = Group.objects.get_or_create(name="Parents")

        teacher_permissions = Permission.objects.filter(
            codename__in=[
                "add_course",
                "change_course",
                "delete_course",
                "view_course",
                "add_coursemodule",
                "change_coursemodule",
                "delete_coursemodule",
                "view_coursemodule",
                "add_lesson",
                "change_lesson",
                "delete_lesson",
                "view_lesson",
                "add_lessonblock",
                "change_lessonblock",
                "delete_lessonblock",
                "view_lessonblock",
            ]
        )
        teacher_group.permissions.set(teacher_permissions)

        student_permissions = Permission.objects.filter(
            codename__in=["view_course", "view_lesson", "view_newspost", "view_achievement", "view_review"]
        )
        student_group.permissions.set(student_permissions)
        parent_group.permissions.set(student_permissions)

        admin, _ = user_model.objects.get_or_create(
            email="admin@kvantorium.local",
            defaults={"is_staff": True, "is_superuser": True, "role": user_model.Role.ADMIN},
        )
        admin.role = user_model.Role.ADMIN
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password("Kv@123456")
        admin.save(update_fields=["role", "is_staff", "is_superuser", "password"])
        admin.groups.set([admin_group])

        teacher, _ = user_model.objects.get_or_create(
            email="teacher@kvantorium.local",
            defaults={
                "first_name": "Иван",
                "last_name": "Ковалев",
                "is_staff": True,
                "role": user_model.Role.TEACHER,
            },
        )
        teacher.first_name = "Иван"
        teacher.last_name = "Ковалев"
        teacher.role = user_model.Role.TEACHER
        teacher.is_staff = True
        teacher.set_password("Kv@123456")
        teacher.save(update_fields=["first_name", "last_name", "role", "is_staff", "password"])
        teacher.groups.set([teacher_group])

        student, _ = user_model.objects.get_or_create(
            email="student@kvantorium.local",
            defaults={"first_name": "Арина", "last_name": "Петрова", "role": user_model.Role.STUDENT},
        )
        student.first_name = "Арина"
        student.last_name = "Петрова"
        student.role = user_model.Role.STUDENT
        student.set_password("Kv@123456")
        student.save(update_fields=["first_name", "last_name", "role", "password"])
        student.groups.set([student_group])

        parent, _ = user_model.objects.get_or_create(
            email="parent@kvantorium.local",
            defaults={"first_name": "Мария", "last_name": "Петрова", "role": user_model.Role.PARENT},
        )
        parent.first_name = "Мария"
        parent.last_name = "Петрова"
        parent.role = user_model.Role.PARENT
        parent.set_password("Kv@123456")
        parent.save(update_fields=["first_name", "last_name", "role", "password"])
        parent.groups.set([parent_group])

        courses_data = [
            {
                "title": "Python для начинающих",
                "short_description": "Переменные, условия, циклы и функции на простых учебных задачах.",
                "description": _txt(
                    """
                    Курс для уверенного старта в программировании.
                    Каждый урок включает теорию, пример кода и задание.
                    """
                ),
                "tags": "Python, Начинающий",
                "modules": [
                    {
                        "title": "Базовый синтаксис",
                        "lessons": [
                            {
                                "title": "Первая программа",
                                "summary": "Пишем первое приложение и учимся читать ошибки.",
                                "blocks": [
                                    {
                                        "type": "text",
                                        "payload": {
                                            "text": "<p>Python выполняет код построчно. Начнем с вывода текста в консоль.</p>",
                                        },
                                    },
                                    {
                                        "type": "code",
                                        "language": "python",
                                        "payload": {"code": "print('Hello, Kvantorium!')"},
                                    },
                                    {
                                        "type": "image",
                                        "payload": {
                                            "url": "/static/img/lesson/python-vars.svg",
                                            "caption": "Пример результата выполнения программы",
                                        },
                                    },
                                    {
                                        "type": "file",
                                        "payload": {"url": "/static/files/python-cheatsheet.txt"},
                                    },
                                ],
                            },
                            {
                                "title": "Переменные и типы данных",
                                "summary": "Работаем со строками, числами и логическими выражениями.",
                                "blocks": [
                                    {
                                        "type": "text",
                                        "payload": {
                                            "text": "<p>Тип в Python определяется автоматически на основе значения.</p>",
                                        },
                                    },
                                    {
                                        "type": "code",
                                        "language": "python",
                                        "payload": {
                                            "code": _txt(
                                                """
                                                name = "Ari"
                                                age = 12
                                                is_student = True
                                                print(name, age, is_student)
                                                """
                                            )
                                        },
                                    },
                                    {"type": "video", "payload": {"url": "https://www.youtube.com/embed/rfscVS0vtbw"}},
                                ],
                            },
                        ],
                    },
                    {
                        "title": "Условия и циклы",
                        "lessons": [
                            {
                                "title": "Оператор if",
                                "summary": "Принимаем решения в программе через ветвления.",
                                "blocks": [
                                    {
                                        "type": "text",
                                        "payload": {
                                            "text": "<p>Условие позволяет выполнять код только при нужном значении выражения.</p>",
                                        },
                                    },
                                    {
                                        "type": "code",
                                        "language": "python",
                                        "payload": {
                                            "code": _txt(
                                                """
                                                score = 83
                                                if score >= 80:
                                                    print("Отлично!")
                                                else:
                                                    print("Пробуем еще")
                                                """
                                            )
                                        },
                                    },
                                ],
                            },
                            {
                                "title": "Циклы for и while",
                                "summary": "Повторяем действия и автоматизируем рутину.",
                                "blocks": [
                                    {
                                        "type": "text",
                                        "payload": {
                                            "text": "<p>for удобен для коллекций, while - для повторений по условию.</p>",
                                        },
                                    },
                                    {
                                        "type": "code",
                                        "language": "python",
                                        "payload": {"code": _txt("for i in range(1, 6):\n    print(i)")},
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            {
                "title": "Scratch: первые игры",
                "short_description": "Создаем интерактивные мини-игры и анимации в визуальной среде.",
                "description": "Курс для детей 8-11 лет: события, циклы, переменные и логика игры.",
                "tags": "Scratch, Junior",
                "modules": [
                    {
                        "title": "Знакомство со сценой",
                        "lessons": [
                            {
                                "title": "Двигаем героя по сцене",
                                "summary": "Настроим управление спрайтом с клавиатуры.",
                                "blocks": [
                                    {
                                        "type": "text",
                                        "payload": {
                                            "text": "<p>Подключи блоки событий и движения, чтобы персонаж реагировал на стрелки.</p>",
                                        },
                                    },
                                    {
                                        "type": "image",
                                        "payload": {
                                            "url": "/static/img/lesson/scratch-stage.svg",
                                            "caption": "Сцена и базовая схема управления",
                                        },
                                    },
                                ],
                            },
                            {
                                "title": "Собираем очки",
                                "summary": "Добавим счетчик и случайные объекты.",
                                "blocks": [
                                    {
                                        "type": "text",
                                        "payload": {
                                            "text": "<p>Создай переменную score и увеличивай ее при касании предмета.</p>",
                                        },
                                    },
                                    {"type": "video", "payload": {"url": "https://www.youtube.com/embed/jXUZaf5D12Q"}},
                                ],
                            },
                        ],
                    },
                    {
                        "title": "Игровая механика",
                        "lessons": [
                            {
                                "title": "Таймер и уровни",
                                "summary": "Добавляем ограничения времени и усложнение игры.",
                                "blocks": [
                                    {
                                        "type": "text",
                                        "payload": {
                                            "text": "<p>Ограничь время раунда до 60 секунд и ускоряй объекты каждые 10 секунд.</p>",
                                        },
                                    }
                                ],
                            }
                        ],
                    },
                ],
            },
            {
                "title": "App Inventor: мобильные приложения",
                "short_description": "Собираем Android-приложения без сложного кода.",
                "description": "Делаем интерфейс, события и простую бизнес-логику через визуальные блоки.",
                "tags": "App Inventor, Mobile",
                "modules": [
                    {
                        "title": "Интерфейс приложения",
                        "lessons": [
                            {
                                "title": "Экран и компоненты",
                                "summary": "Добавляем кнопки, текст и изображения в мобильный экран.",
                                "blocks": [
                                    {
                                        "type": "text",
                                        "payload": {
                                            "text": "<p>Создай экран приветствия: заголовок, картинка и кнопка перехода.</p>",
                                        },
                                    },
                                    {
                                        "type": "image",
                                        "payload": {
                                            "url": "/static/img/lesson/appinventor-ui.svg",
                                            "caption": "Базовый макет мобильного экрана",
                                        },
                                    },
                                ],
                            }
                        ],
                    },
                    {
                        "title": "Логика блоков",
                        "lessons": [
                            {
                                "title": "Обработка нажатий",
                                "summary": "Соединяем интерфейс и поведение через события.",
                                "blocks": [
                                    {
                                        "type": "code",
                                        "language": "pseudo",
                                        "payload": {
                                            "code": _txt(
                                                """
                                                when ButtonStart.Click do
                                                  set LabelStatus.Text to "Готово!"
                                                """
                                            )
                                        },
                                    },
                                    {"type": "video", "payload": {"url": "https://www.youtube.com/embed/2A2XBoxtcUA"}},
                                ],
                            }
                        ],
                    },
                ],
            },
            {
                "title": "Web Start: HTML + CSS",
                "short_description": "Делаем первую веб-страницу и знакомимся с версткой.",
                "description": "Теги, структура документа, базовая стилизация и работа со шрифтами.",
                "tags": "Web, HTML, CSS",
                "modules": [
                    {
                        "title": "Основы HTML",
                        "lessons": [
                            {
                                "title": "Каркас страницы",
                                "summary": "Создаем структуру index.html с заголовками и блоками.",
                                "blocks": [
                                    {
                                        "type": "text",
                                        "payload": {
                                            "text": "<p>Любая HTML-страница начинается с doctype и базовой структуры head/body.</p>",
                                        },
                                    },
                                    {
                                        "type": "code",
                                        "language": "html",
                                        "payload": {
                                            "code": _txt(
                                                """
                                                <!doctype html>
                                                <html lang="ru">
                                                  <head><title>My page</title></head>
                                                  <body><h1>Hello!</h1></body>
                                                </html>
                                                """
                                            )
                                        },
                                    },
                                ],
                            },
                            {
                                "title": "Первые стили",
                                "summary": "Добавляем цвета, отступы и шрифты.",
                                "blocks": [
                                    {
                                        "type": "code",
                                        "language": "css",
                                        "payload": {
                                            "code": _txt(
                                                """
                                                body { font-family: sans-serif; margin: 0; }
                                                h1 { color: #3d8ed8; }
                                                """
                                            )
                                        },
                                    }
                                ],
                            },
                        ],
                    }
                ],
            },
            {
                "title": "Алгоритмы и олимпиадный старт",
                "short_description": "Логика, массивы, разбор задач и стратегия решения.",
                "description": "Подготовительный курс для олимпиад и технических собеседований школьного уровня.",
                "tags": "Алгоритмы, Olympiad",
                "modules": [
                    {
                        "title": "Базовые стратегии",
                        "lessons": [
                            {
                                "title": "Оценка сложности",
                                "summary": "Разбираем O(n), O(n^2) и влияние на скорость программы.",
                                "blocks": [
                                    {
                                        "type": "text",
                                        "payload": {
                                            "text": "<p>Сложность показывает, как растет время выполнения при увеличении входных данных.</p>",
                                        },
                                    },
                                    {
                                        "type": "code",
                                        "language": "python",
                                        "payload": {
                                            "code": _txt(
                                                """
                                                def linear(arr):
                                                    for x in arr:
                                                        if x == 0:
                                                            return True
                                                    return False
                                                """
                                            )
                                        },
                                    },
                                ],
                            }
                        ],
                    }
                ],
            },
        ]

        created_courses = []
        for course_data in courses_data:
            course, _ = Course.objects.get_or_create(
                title=course_data["title"],
                defaults={
                    "short_description": course_data["short_description"],
                    "description": course_data["description"],
                    "tags": course_data["tags"],
                    "status": "published",
                    "created_by": teacher,
                },
            )
            course.short_description = course_data["short_description"]
            course.description = course_data["description"]
            course.tags = course_data["tags"]
            course.status = "published"
            course.created_by = teacher
            course.save()
            created_courses.append(course)

            for module_order, module_data in enumerate(course_data["modules"], start=1):
                module, _ = CourseModule.objects.get_or_create(
                    course=course,
                    title=module_data["title"],
                    defaults={"order": module_order},
                )
                module.order = module_order
                module.save(update_fields=["order"])

                for lesson_order, lesson_data in enumerate(module_data["lessons"], start=1):
                    lesson, _ = Lesson.objects.get_or_create(
                        module=module,
                        title=lesson_data["title"],
                        defaults={
                            "summary": lesson_data["summary"],
                            "order": lesson_order,
                            "is_published": True,
                        },
                    )
                    lesson.summary = lesson_data["summary"]
                    lesson.order = lesson_order
                    lesson.is_published = True
                    lesson.save(update_fields=["summary", "order", "is_published"])

                    lesson.blocks.all().delete()
                    for block_order, block_data in enumerate(lesson_data["blocks"], start=1):
                        LessonBlock.objects.create(
                            lesson=lesson,
                            type=block_data["type"],
                            order=block_order,
                            payload=block_data.get("payload", {}),
                            language=block_data.get("language", ""),
                        )

        for course in created_courses:
            Enrollment.objects.get_or_create(user=student, course=course)
            Enrollment.objects.get_or_create(user=parent, course=course)

        news_items = [
            (
                "Старт новой программы Python",
                "start-python",
                "Открыт новый поток курса Python для начинающих.",
                "<p>Программа рассчитана на 8 недель и включает финальный мини-проект.</p>",
            ),
            (
                "Открыт набор в Scratch-группу",
                "scratch-group-open",
                "Новая группа для детей 8-11 лет начинает обучение в этом месяце.",
                "<p>На курсе дети создадут собственную игру и защитят ее на демо-дне.</p>",
            ),
            (
                "День открытых дверей",
                "open-day",
                "Приглашаем родителей и учеников познакомиться с программами центра.",
                "<p>Будут мастер-классы по Python, Scratch и мобильной разработке.</p>",
            ),
            (
                "Итоги месяца",
                "month-results",
                "Ученики защитили 14 мини-проектов по программированию.",
                "<p>Лучшие проекты попадут в портфолио выпускников и на витрину достижений.</p>",
            ),
            (
                "Новый курс по веб-разработке",
                "web-course-launch",
                "Запускаем модуль по HTML/CSS для учеников 12+.",
                "<p>В программе: верстка лендинга, компоненты интерфейса и публикация проекта.</p>",
            ),
            (
                "Подготовка к олимпиаде",
                "olympiad-prep",
                "Открыты дополнительные занятия по алгоритмам и задачам.",
                "<p>Группы стартуют в выходные, запись доступна через личный кабинет.</p>",
            ),
            (
                "Победы на городском фестивале IT-проектов",
                "city-it-festival",
                "Команда Кванториума заняла 2 призовых места в двух номинациях.",
                "<p>Ребята представили веб-портал школьного клуба и мобильный помощник для расписания.</p>",
            ),
            (
                "Летняя школа программирования",
                "summer-school",
                "Открыт ранний набор в летний интенсив 2026 года.",
                "<p>Формат: 3 занятия в неделю, проектная работа и публичная защита.</p>",
            ),
        ]
        for index, (title, slug, summary, body) in enumerate(news_items):
            NewsPost.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "summary": summary,
                    "body": body,
                    "published_at": timezone.now() - timedelta(days=index),
                    "status": "published",
                },
            )

        achievements_items = [
            (
                "Победа на региональном хакатоне",
                "2025",
                "Хакатоны",
                "Команда Кванториума взяла 1 место в номинации 'Образовательный продукт'.",
            ),
            (
                "Приз зрительских симпатий",
                "2024",
                "Робототехника",
                "Проект учеников по робототехнике получил специальный приз жюри.",
            ),
            (
                "Лучший учебный проект года",
                "2025",
                "Программирование",
                "Сайт школьного клуба признан лучшим учебным веб-проектом.",
            ),
            (
                "Финалисты ИТ-чемпионата",
                "2024",
                "Соревнования",
                "Сразу три команды вошли в топ-10 городского чемпионата.",
            ),
            (
                "Сертификаты от партнера",
                "2025",
                "Партнерство",
                "20 учеников получили сертификаты по базовому Python.",
            ),
            (
                "Лучший наставник сезона",
                "2025",
                "Команда",
                "Преподаватель центра получил награду за вклад в STEM-образование.",
            ),
            (
                "Приз за UX-прототип",
                "2026",
                "Дизайн",
                "Ученики старшей группы представили лучший прототип LMS-модуля на школьном форуме.",
            ),
        ]
        for title, year, category, description in achievements_items:
            Achievement.objects.update_or_create(
                title=title,
                defaults={"year": year, "category": category, "description": description},
            )

        reviews_items = [
            ("Алексей", "parent", 5, "Ребенок в восторге от занятий и начал сам писать небольшие программы."),
            ("Ирина", "student", 5, "Очень нравится формат: теория коротко, затем сразу практика."),
            ("Ольга", "parent", 5, "Хорошая подача материала и внимательное отношение преподавателей."),
            ("Егор", "student", 4, "Больше всего понравились задания с мини-играми и проектами."),
            ("Светлана", "parent", 5, "Отличная платформа: видно прогресс и домашние задания."),
            ("Михаил", "student", 5, "Наконец-то понял, как работают циклы и условия."),
            ("Дарья", "alumni", 5, "После курса стало проще учиться в колледже на ИТ-направлении."),
            ("Никита", "student", 4, "Удобно, что можно пересматривать уроки и повторять материал."),
            ("Татьяна", "parent", 5, "Ребенок стал увереннее на школьной информатике."),
            ("Андрей", "student", 5, "Понравился курс по веб-разработке, уже сделал свой мини-сайт."),
        ]
        for name, author_type, rating, text in reviews_items:
            Review.objects.update_or_create(
                name=name,
                author_type=author_type,
                text=text,
                defaults={"rating": rating, "is_approved": True},
            )

        ContactInfo.objects.update_or_create(
            address="г. Барнаул, проспект Ленина, 40",
            defaults={
                "phone": "+7 (3852) 12-34-56",
                "email": "info@kvantorium.local",
                "schedule": "Пн-Пт 09:00-18:00",
                "map_url": "",
            },
        )

        if created_courses:
            completed_lessons = Lesson.objects.filter(module__course=created_courses[0], is_published=True).order_by("order")[:2]
            for lesson in completed_lessons:
                LessonProgressEvent.objects.get_or_create(user=student, lesson=lesson, event_type="done")
            update_course_progress(student, created_courses[0])

            for course in created_courses[1:]:
                update_course_progress(student, course)
                update_course_progress(parent, course)
            update_course_progress(parent, created_courses[0])

        self.stdout.write(self.style.SUCCESS("Demo data seeded: users, courses, lessons, progress, news, achievements, reviews."))
