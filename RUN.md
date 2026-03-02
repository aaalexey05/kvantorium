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
- Суперпользователь (создан):
  - email: admin@kvantorium.local
  - password: Kv@123456

## Полезные команды
- Остановить: `docker compose down`
- Остановить с очисткой БД: `docker compose down -v`
- Логи web: `docker compose logs -f web`
- Применить миграции вручную: `docker compose run --rm web python src/manage.py migrate`
- Создать нового суперпользователя: `docker compose run --rm web python src/manage.py createsuperuser`

## Что проверить
- Публичные страницы: `/`, `/courses/`, деталь курса/урока, `/news/`, `/achievements/`, `/reviews/`, `/contacts/`.
- HTMX: кнопка «Записаться» и «Отметить как пройдено» обновляют интерфейс без перезагрузки.
- Админка `/admin/`: создание курсов/модулей/уроков/блоков, новостей, достижений, контактов; модерация отзывов. Статические файлы админки отдаются корректно (проверено).

## Описание проекта (кратко)
Django 5 + PostgreSQL LMS: курсы→модули→уроки→блоки (текст/код/картинка/видео/файл), записи на курс, прогресс, практика (заготовка), новости, достижения, отзывы, контакты. Frontend — Django templates + HTMX/Alpine + Prism, тёмный UI. Контейнеры web/db/nginx, конфиг через `.env` (загружается через python-dotenv). Стандартный интерфейс админ-панели сохранён.
