# Calendar API
Calendar API предоставляет функциональность для создания и управления напоминаниями.


## Возможности:
- cоздание, редактирование, чтение и удаление заданий записей;
- аутентификация и авторизация JWT;
- агрегация событий по дням за месяц;
- возможность напоминаний о событиях на почту;

## Используемые технологии:
- Python;
- Django;
- Django Rest Framework;
- Django ORM
- PostgreSQL 
- Docker containers;
- Redis;
- Celery.

## Использование

1) <strong>Клонируем репозиторий: </strong>

   ```
   git@github.com:56lesha/Calendar_DRF.git
   ```

3) <strong>Создаём в корне проекта файл db_keys.txt со следующим содержимым: </strong>
   ```
   POSTGRES_DB='your db name'
   POSTGRES_USER='your db user'
   POSTGRES_PASSWORD='your db password'
   POSTGRES_HOST=db
   POSTGRES_PORT=5432
   ```
3) <strong>Собираем проект</strong>
   ```
   docker-compose build
   ```
4) <strong>Запускаем проект</strong>
   ``` 
   docker-compose up 
   ```
5) <strong>Переходим по ссылке:</strong>
   ```
   http://localhost:8000/
   ```

   🚀 <strong>Приложение запущено и готово к использованию !


