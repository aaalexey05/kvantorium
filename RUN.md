# RUNBOOK: эксплуатация KVANTORIUM LMS

Документ для разработчиков и администраторов системы.

## 1. Область применения

Runbook покрывает:

- запуск и остановку сервиса;
- обновление версии проекта;
- проверку здоровья и диагностику;
- резервное копирование и восстановление;
- базовые меры безопасности в эксплуатации.

Быстрый старт разработки: `README.md`.

---

## 2. Контуры и переменные окружения

## 2.1. Локальный контур (dev)

- Django: `config.settings.dev`
- БД: PostgreSQL в Docker
- Старт через `docker compose`

## 2.2. Production-контур

- Django: `config.settings.prod`
- Gunicorn + Nginx
- HTTPS-флаги активируются через `DJANGO_USE_HTTPS=True`

## 2.3. Минимальный `.env`

```env
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.ru,127.0.0.1,localhost
DJANGO_USE_HTTPS=False

POSTGRES_DB=kvantorium
POSTGRES_USER=kv_user
POSTGRES_PASSWORD=strong-password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

---

## 3. Стандартные операции

## 3.1. Запуск

```bash
docker compose up -d --build
```

## 3.2. Остановка

```bash
docker compose down
```

С удалением volume БД (только для dev):

```bash
docker compose down -v
```

## 3.3. Проверка статуса

```bash
docker compose ps
docker compose logs --tail 200 web
docker compose logs --tail 200 nginx
docker compose logs --tail 200 db
curl -f http://127.0.0.1:8000/health/
```

## 3.4. Миграции/статика вручную

```bash
docker compose run --rm web python src/manage.py migrate
docker compose run --rm web python src/manage.py collectstatic --noinput
```

## 3.5. Создание администратора

```bash
docker compose run --rm web python src/manage.py createsuperuser
```

## 3.6. Тестовое наполнение

```bash
docker compose run --rm web python src/manage.py seed_demo
```

Важно: после генерации тестовых пользователей сменить пароли и удалить ненужные учетные записи.

---

## 4. Процедура обновления (deploy)

```bash
git pull
docker compose up -d --build
docker compose run --rm web python src/manage.py migrate
docker compose run --rm web python src/manage.py collectstatic --noinput
curl -f http://127.0.0.1:8000/health/
```

После деплоя проверить:

- `/`;
- `/admin/`;
- `/courses/`;
- `/static/css/main.css` (должен отдавать `200`).

---

## 5. Инциденты и диагностика

## 5.1. Ошибка статики (CSS/JS 404)

Симптом:

- интерфейс без стилей;
- в логах nginx `open() ... /static/... failed (2: No such file or directory)`.

Проверка и фиксация:

```bash
docker compose logs --tail 200 nginx
docker compose exec web ls -la /app/src/staticfiles
docker compose run --rm web python src/manage.py collectstatic --noinput
docker compose restart nginx
```

Проверить nginx alias на `/var/www/static/` и корректный volume `./src/staticfiles:/var/www/static:ro`.

## 5.2. CSRF 403 на логине

Симптом:

- `Forbidden (CSRF cookie not set.)`

Проверить:

- `DJANGO_USE_HTTPS` соответствует реальному протоколу;
- при HTTP: `DJANGO_USE_HTTPS=False`;
- при HTTPS: `DJANGO_USE_HTTPS=True` + корректный proxy header.

Применение:

```bash
docker compose restart web
```

## 5.3. База недоступна

```bash
docker compose ps
docker compose logs --tail 200 db
docker compose exec db pg_isready -U "$POSTGRES_USER"
```

---

## 6. План резервного копирования

## 6.1. Цели

- целевой `RPO`: до 24 часов;
- целевой `RTO`: до 2 часов.

## 6.2. Что резервируем

1. PostgreSQL (обязательно).
2. Директорию `src/media` (обязательно).
3. Файлы конфигурации (`.env`, `docker-compose.yml`, nginx конфиг) (обязательно).

## 6.3. Периодичность

- БД: ежедневно ночью.
- `media`: ежедневно инкрементально/еженедельно полный архив.
- Конфиги: при каждом изменении + ежедневный snapshot.

## 6.4. Пример команд backup

### Бэкап БД

```bash
mkdir -p backups
TS=$(date +%F_%H-%M)
docker compose exec -T db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" > "backups/db_${TS}.sql"
```

### Бэкап media

```bash
TS=$(date +%F_%H-%M)
tar -czf "backups/media_${TS}.tar.gz" -C src media
```

### Ротация (пример)

```bash
find backups -type f -name 'db_*.sql' -mtime +7 -delete
find backups -type f -name 'media_*.tar.gz' -mtime +30 -delete
```

---

## 7. Восстановление

## 7.1. Восстановление БД из SQL-дампа

```bash
cat backups/db_YYYY-MM-DD_HH-MM.sql | docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

Если требуется чистое восстановление:

```bash
docker compose exec -T db psql -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE IF EXISTS $POSTGRES_DB;"
docker compose exec -T db psql -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE $POSTGRES_DB;"
cat backups/db_YYYY-MM-DD_HH-MM.sql | docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

## 7.2. Восстановление media

```bash
tar -xzf backups/media_YYYY-MM-DD_HH-MM.tar.gz -C src
```

## 7.3. Финальные шаги после restore

```bash
docker compose run --rm web python src/manage.py migrate
docker compose run --rm web python src/manage.py collectstatic --noinput
docker compose restart web nginx
curl -f http://127.0.0.1:8000/health/
```

Smoke-check:

- главная страница;
- логин в админку;
- список курсов;
- открытие урока;
- отправка отзыва.

---

## 8. Эксплуатационная безопасность

- не хранить пароли/ключи в git и документации;
- ограничить SSH-доступ по IP и отключить password auth после перехода на ключи;
- периодически ротировать `DJANGO_SECRET_KEY` и пароли БД;
- включать `DJANGO_USE_HTTPS=True` только при реальном HTTPS;
- регулярно обновлять базовые Docker-образы.

---

## 9. Регламент еженедельной проверки

1. Проверить `docker compose ps`.
2. Проверить `/health/`.
3. Просмотреть логи `web/nginx/db` на ошибки.
4. Проверить успешность backup за последние 7 дней.
5. Проверить объем диска и размер volume БД.
6. Проверить доступность админки и статических файлов.

