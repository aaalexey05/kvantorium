# KVANTORIUM LMS

Единая LMS-платформа для учебного центра: курсы, модули, уроки, прогресс, отзывы, новости, достижения и ролевые кабинеты.

## Быстрый старт на своем компьютере

### 1) Требования

- Docker Desktop 4+
- Docker Compose v2
- Git

### 2) Установка и запуск (Docker-first)

```bash
git clone <repo_url>
cd kvantorium
cp .env.example .env
docker compose up -d --build
```

Откроется:

- приложение: `http://127.0.0.1:8000`
- через nginx: `http://127.0.0.1:80`
- health-check: `http://127.0.0.1:8000/health/`
- админка: `http://127.0.0.1:8000/admin/`

### 3) Миграции, демо-данные, суперпользователь

```bash
# если нужно вручную
docker compose run --rm web python src/manage.py migrate

# демо-наполнение (курсы/уроки/новости/достижения/отзывы)
docker compose run --rm web python src/manage.py seed_demo

# создать своего администратора
docker compose run --rm web python src/manage.py createsuperuser
```

Полный runbook эксплуатации, инцидентов и резервного копирования: `RUN.md`.

---

## Функциональность и роли

### Гость

- просмотр главной, курсов, новостей, достижений, отзывов, контактов;
- регистрация/вход.

### Ученик

- запись на курс/отписка;
- просмотр уроков;
- отметка урока как пройденного;
- просмотр прогресса в профиле;
- отправка отзывов.

### Преподаватель

- создание/редактирование своих курсов;
- управление модулями, уроками, блоками контента (`text`, `code`, `image`, `video`, `file`);
- шаблоны уроков;
- drag&drop сортировка блоков;
- дублирование блоков;
- автосохранение черновика;
- предпросмотр урока;
- статистика по курсам.

### Администратор

- управление пользователями и ролями;
- управление всеми курсами;
- новости и достижения (CRUD);
- контакты и карта;
- доступ к Django Admin.

---

## Словарь данных (таблицы, поля, типы, комментарии)

Ниже перечислены бизнес-таблицы проекта. Служебные таблицы Django вынесены отдельным блоком.

### `accounts_user`

| Поле | Тип | Комментарий |
|---|---|---|
| id | BigAutoField | PK |
| password | CharField | хэш пароля |
| last_login | DateTimeField, null | дата последнего входа |
| is_superuser | BooleanField | полный доступ |
| first_name | CharField | имя |
| last_name | CharField | фамилия |
| is_staff | BooleanField | доступ к staff-интерфейсам |
| is_active | BooleanField | активность учетной записи |
| date_joined | DateTimeField | дата регистрации |
| email | EmailField, unique | логин пользователя |
| role | CharField(choices) | `student` / `parent` / `teacher` / `admin` |

### `courses_course`

| Поле | Тип | Комментарий |
|---|---|---|
| id | BigAutoField | PK |
| title | CharField(200) | название курса |
| slug | SlugField, unique | URL-идентификатор |
| short_description | TextField | краткое описание |
| description | TextField | подробное описание |
| age_group | CharField(50) | возрастная группа |
| level | CharField(50) | уровень |
| tags | CharField(200) | теги |
| cover | ImageField, null/blank | обложка |
| status | CharField(choices) | `draft` / `published` |
| created_by_id | FK -> accounts_user | автор курса |
| created_at | DateTimeField | дата создания |
| updated_at | DateTimeField | дата обновления |

### `courses_coursemodule`

| Поле | Тип | Комментарий |
|---|---|---|
| id | BigAutoField | PK |
| course_id | FK -> courses_course | курс |
| title | CharField(200) | название модуля |
| order | PositiveIntegerField | порядок в курсе |

### `courses_lesson`

| Поле | Тип | Комментарий |
|---|---|---|
| id | BigAutoField | PK |
| module_id | FK -> courses_coursemodule | модуль |
| title | CharField(200) | название урока |
| summary | TextField | краткое содержание |
| order | PositiveIntegerField | порядок в модуле |
| is_published | BooleanField | опубликован ли урок |

### `courses_lessonblock`

| Поле | Тип | Комментарий |
|---|---|---|
| id | BigAutoField | PK |
| lesson_id | FK -> courses_lesson | урок |
| type | CharField(choices) | тип блока (`text`, `code`, `image`, `video`, `file`) |
| order | PositiveIntegerField | порядок блока |
| payload | JSONField | содержимое блока |
| language | CharField(30) | язык кода для `code` |

### `courses_enrollment`

| Поле | Тип | Комментарий |
|---|---|---|
| id | BigAutoField | PK |
| user_id | FK -> accounts_user | пользователь |
| course_id | FK -> courses_course | курс |
| created_at | DateTimeField | дата записи |

Ограничение: `unique_together(user_id, course_id)`.

### `practice_practicetask`

| Поле | Тип | Комментарий |
|---|---|---|
| id | BigAutoField | PK |
| lesson_id | FK -> courses_lesson | урок |
| title | CharField(200) | название задания |
| description | TextField | описание |
| task_type | CharField(choices) | `quiz`, `code`, `text` |
| payload | JSONField | данные задачи |
| is_active | BooleanField | активность задания |

### `practice_taskattempt`

| Поле | Тип | Комментарий |
|---|---|---|
| id | BigAutoField | PK |
| task_id | FK -> practice_practicetask | задание |
| user_id | FK -> accounts_user | пользователь |
| status | CharField(20) | статус попытки |
| score | FloatField | балл |
| submitted_payload | JSONField | отправленные данные |
| created_at | DateTimeField | дата попытки |

### `progress_courseprogress`

| Поле | Тип | Комментарий |
|---|---|---|
| id | BigAutoField | PK |
| user_id | FK -> accounts_user | пользователь |
| course_id | FK -> courses_course | курс |
| percent | FloatField | прогресс в % |
| updated_at | DateTimeField | пересчет прогресса |

Ограничение: `unique_together(user_id, course_id)`.

### `progress_lessonprogressevent`

| Поле | Тип | Комментарий |
|---|---|---|
| id | BigAutoField | PK |
| user_id | FK -> accounts_user | пользователь |
| lesson_id | FK -> courses_lesson | урок |
| event_type | CharField(choices) | `read`, `watch`, `done` |
| created_at | DateTimeField | время события |

### `news_newspost`

| Поле | Тип | Комментарий |
|---|---|---|
| id | BigAutoField | PK |
| title | CharField(200) | заголовок |
| slug | SlugField, unique | URL |
| summary | TextField | анонс |
| body | TextField | текст новости |
| published_at | DateTimeField | дата публикации |
| status | CharField(20) | статус публикации |
| image | ImageField, null/blank | иллюстрация |

### `achievements_achievement`

| Поле | Тип | Комментарий |
|---|---|---|
| id | BigAutoField | PK |
| title | CharField(200) | заголовок |
| description | TextField | описание |
| year | CharField(10) | год |
| category | CharField(100) | категория |
| media | ImageField, null/blank | изображение |
| created_at | DateTimeField | дата добавления |

### `reviews_review`

| Поле | Тип | Комментарий |
|---|---|---|
| id | BigAutoField | PK |
| name | CharField(120) | имя автора |
| author_type | CharField(choices) | `parent`, `student`, `alumni` |
| text | TextField | текст отзыва |
| rating | PositiveSmallIntegerField | оценка |
| is_approved | BooleanField | модерация |
| created_at | DateTimeField | дата создания |

### `core_contactinfo`

| Поле | Тип | Комментарий |
|---|---|---|
| id | BigAutoField | PK |
| address | CharField(255) | адрес |
| phone | CharField(50) | телефон |
| email | EmailField | email |
| map_url | URLField(2048) | ссылка карты (опц.) |
| schedule | CharField(255) | график |
| created_at | DateTimeField | дата создания |

### Служебные таблицы Django (инфраструктурные)

| Таблица | Назначение |
|---|---|
| `django_migrations` | история миграций |
| `django_content_type` | реестр моделей |
| `auth_permission` | объектные и модельные permissions |
| `auth_group` / `auth_group_permissions` | группы и их права |
| `accounts_user_groups` / `accounts_user_user_permissions` | связи пользователя с группами/правами |
| `django_admin_log` | журнал действий в admin |
| `django_session` | серверные сессии |

---

## Структура проекта: директории, файлы, ответственность

```text
kvantorium/
├─ src/
│  ├─ apps/
│  │  ├─ accounts/        # auth, регистрация, профиль, роли
│  │  ├─ courses/         # курсы/модули/уроки/блоки/запись
│  │  ├─ progress/        # прогресс и события прохождения
│  │  ├─ practice/        # практические задания и попытки
│  │  ├─ dashboard/       # role-based панели admin/teacher
│  │  ├─ news/            # новости
│  │  ├─ achievements/    # достижения
│  │  ├─ reviews/         # отзывы и модерация
│  │  ├─ core/            # главная, контакты, health, map utils
│  │  └─ audit/           # задел под аудит-действия
│  ├─ config/
│  │  ├─ settings/
│  │  │  ├─ base.py       # базовые настройки
│  │  │  ├─ dev.py        # dev-конфигурация
│  │  │  └─ prod.py       # prod-конфигурация
│  │  ├─ urls.py          # корневые маршруты
│  │  └─ wsgi.py          # WSGI entrypoint
│  ├─ templates/          # Django templates
│  ├─ static/             # исходные статические файлы
│  ├─ staticfiles/        # collectstatic output
│  └─ media/              # пользовательские upload-файлы
├─ deploy/nginx/          # nginx-конфиги для docker-окружения
├─ Dockerfile
├─ docker-compose.yml
├─ RUN.md                 # эксплуатационный runbook
└─ docs/PROJECT_FULL_SPEC.md
```

---

## Настройки безопасности

### Конфигурация Django

- `SECRET_KEY` берется из `.env` (`DJANGO_SECRET_KEY`), не хранить прод-значение в git.
- `ALLOWED_HOSTS` задается через `DJANGO_ALLOWED_HOSTS`.
- Включен `CsrfViewMiddleware`.
- В прод-режиме cookie-флаги зависят от `DJANGO_USE_HTTPS`:
  - `SESSION_COOKIE_SECURE`
  - `CSRF_COOKIE_SECURE`
- При HTTPS учитывается `SECURE_PROXY_SSL_HEADER`.

### Ролевой доступ

- Критичные действия защищены серверными декораторами и проверками (`admin_required`, `teacher_or_admin_required`).
- Фронтенд-скрытие кнопок используется только как UX-слой, не как защита.

### Операционные практики

- не публиковать `.env`;
- не хранить пароли в документации;
- менять пароли тестовых пользователей после `seed_demo`;
- ограничивать доступ к SSH и БД по IP.

---

## Runbook эксплуатации

Операционные процедуры вынесены в `RUN.md`:

- запуск/остановка/обновление;
- health-check и диагностика;
- восстановление после типовых инцидентов;
- backup/restore PostgreSQL и media;
- чек-листы перед релизом и после релиза.

---

## План резервного копирования и восстановления (кратко)

### Резервное копирование

- Ежедневный `pg_dump` базы (ночью).
- Еженедельный полный архив `media/`.
- Хранение минимум 7 ежедневных и 4 еженедельных копий.
- Хранение копий минимум в двух местах (сервер + внешний storage).

### Восстановление

- Восстановить пустую БД.
- Применить дамп `pg_restore`/`psql`.
- Развернуть архив `media/`.
- Запустить миграции и smoke-check.

Подробные команды, шаблон cron и регламент RPO/RTO: `RUN.md`.

---

## Дополнительная документация

- Полное описание проекта, процессов и экономики: `docs/PROJECT_FULL_SPEC.md`
- Эксплуатация и восстановление: `RUN.md`
