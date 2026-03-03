# Запуск проекта «Кванториум 22» (Docker-first)

## Окружение
1) Установите Docker Desktop.
2) Скопируйте env: `cp .env.example .env` (по умолчанию: DB=kvantorium, USER=kv_user, PASS=kv_pass, HOST=db).

## Старт стека
```bash
docker compose up -d --build
```
- web запускается в режиме `config.settings.dev`: применяет миграции, собирает статику, стартует Django dev-сервер на 0.0.0.0:8000.
- Сервисы: web (Django), db (PostgreSQL 15), nginx (прокси статика/медиа на 80).

## Доступы
- Приложение: http://127.0.0.1:8000
- Nginx (статик/медиа): http://127.0.0.1:80
- Health: http://127.0.0.1:8000/health/
- Админка (стандартный интерфейс Django): http://127.0.0.1:8000/admin/
- Ролевой роутер: http://127.0.0.1:8000/dashboard/

### Тестовые пользователи (создаются командой `seed_demo`)
- `admin@kvantorium.local` / `Kv@123456` — администратор
- `teacher@kvantorium.local` / `Kv@123456` — преподаватель
- `student@kvantorium.local` / `Kv@123456` — ученик
- `parent@kvantorium.local` / `Kv@123456` — родитель

После логина каждый пользователь попадает на свою стартовую страницу:
- admin → `/dashboard/admin/`
- teacher → `/dashboard/teacher/`
- student/parent → `/accounts/profile/`

Если пользователей нет, создайте их:
```bash
docker compose run --rm web python src/manage.py seed_demo
```

### Что добавляет `seed_demo`
- 5 опубликованных курсов с модулями/уроками
- блоки уроков: `text`, `code`, `image`, `video`, `file`
- записи пользователей на курсы и пример прогресса ученика
- 8 новостей, 7 достижений, набор одобренных отзывов для витрины

## Полезные команды
- Остановить: `docker compose down`
- Остановить с очисткой БД: `docker compose down -v`
- Логи web: `docker compose logs -f web`
- Применить миграции вручную: `docker compose run --rm web python src/manage.py migrate`
- Создать нового суперпользователя: `docker compose run --rm web python src/manage.py createsuperuser`
- Пересоздать тестовые данные: `docker compose run --rm web python src/manage.py seed_demo`

## Что проверить
- Публичные страницы: `/`, `/courses/`, деталь курса/урока, `/news/`, `/achievements/`, `/reviews/`, `/contacts/`.
- HTMX: кнопка «Записаться» и «Отметить как пройдено» обновляют интерфейс без перезагрузки.
- Админка `/admin/`: создание курсов/модулей/уроков/блоков, новостей, достижений, контактов; модерация отзывов. Статические файлы админки отдаются корректно (проверено).
- Проверка devtools probe: `/.well-known/appspecific/com.chrome.devtools.json` должен отдавать `200` JSON.
- Роли:
  - admin: доступны `/dashboard/admin/`, `/dashboard/admin/courses/`, `/dashboard/admin/users/`
  - admin (контент): `/dashboard/admin/news/`, `/dashboard/admin/achievements/`
  - admin (контакты + карта): `/dashboard/admin/contacts/` (адрес обновляет карту в live-preview через HTMX)
  - teacher: доступны `/dashboard/teacher/`, `/dashboard/teacher/courses/`, `/dashboard/teacher/courses/create/`, `/dashboard/teacher/stats/`
  - teacher (наполнение курса): в `/dashboard/teacher/courses/<id>/edit/` можно добавлять модули, уроки и блоки контента (`text`, `code`, `image`, `video`, `file`)
  - student/parent: прямой доступ на admin/teacher страницы должен отдавать `403`

## Описание проекта (кратко)
Django 5 + PostgreSQL LMS: курсы→модули→уроки→блоки (текст/код/картинка/видео/файл), записи на курс, прогресс, практика (заготовка), новости, достижения, отзывы, контакты. Frontend — Django templates + HTMX/Alpine + Prism, тёмный UI. Контейнеры web/db/nginx, конфиг через `.env` (загружается через python-dotenv). Стандартный интерфейс админ-панели сохранён.
