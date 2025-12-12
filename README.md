### Запуск приложения:
Создайте файл `.env` в корне проекта:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=project
DATABASE_URL=postgresql://postgres:postgres@db:5432/project

REDIS_URL=redis://redis:6379/0

SECRET_KEY=your_secret_key
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URL=http://localhost:8000/auth/github/callback

VITE_API_URL=http://localhost:8000
```

Для запуска:
docker-compose up -d --build\

После запуска сервис доступен на: http://localhost:5173/
Документация Swagger: http://localhost:8000/docs


### Модели данных

### Пользователь (`users`):
- `id` — уникальный идентификатор пользователя
- `name` — уникальное имя пользователя (есть валидация: длина 3–32, латиница/цифры/._-)
- `email` — уникальный email пользователя
- `hashed_password` — хэшированный пароль (для локальной авторизации)
- `registration_date` — дата регистрации
- `is_verified` — флаг того, верифицирован пользователь или нет
- `is_admin` — флаг администратора
- `avatar` — аватарка пользователя (опционально)

### Новость (`news`):
- `id` — уникальный идентификатор новости
- `title` — заголовок
- `content` — контент (JSON)
- `publication_date` — дата публикации
- `cover` — обложка (опционально)
- `author_id` — автор новости - внешний ключ к таблице пользователей

### Комментарий (`comments`):
- `id` — уникальный идентификатор комментария
- `text` — текст комментария
- `ppublication_date` — дата публикации
- `news_id` — новость, к которой оставлен комментарий - внешний ключ к таблице новостей
- `author_id` — автор комментария - внешний ключ к таблице пользователей

### Refresh-токены (`refresh_tokens`):
- `id` — уникальный идентификатор сессии
- `user_id` — пользователь (внешний ключ)
- `refresh_token` — токен для обновления access_token
- `user_agent` — информация о клиенте
- `created_at` — дата создания сессии

У вводимого пароля пользователем есть валидация: он должен быть как минимум из 8 символов, минимум 1 заглавная, 1 строчная, 1 цифра, 1 спецсимвол

### Примеры curl запросов:

Создать администратора:
docker-compose exec db psql -U postgres -d web_lab1_db
INSERT INTO users (name, email, is_admin, is_verified, registration_date) 
VALUES ('Admin', 'admin@example.com', TRUE, TRUE, NOW());

Регистрация:
```
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Denis",
       "email": "den@gmail.ru",
       "password": "12345"
     }'
```

Получить токен:
```
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=den@gmail.ru&password=12345"
```

Авторизация через GitHub:
1. Откройте в браузере: http://localhost:8000/auth/github/login
2. Авторизуйтесь на GitHub
3. Вас перенаправит на /auth/github/callback с токенами в JSON

Обновление токена:
```
curl -X POST "http://localhost:8000/auth/refresh" \
     -H "Content-Type: application/json" \
     -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

Просмотр активных сессий:
```
curl -X GET "http://localhost:8000/auth/sessions" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Выход:
```
curl -X POST "http://localhost:8000/auth/logout" \
     -H "Content-Type: application/json" \
     -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

Создать пользователя (может только админ):
```
curl -X POST "http://localhost:8000/users/" \
     -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Denis",
       "email": "den@gmail.ru",
       "password": "123",
       "is_verified": true,
       "avatar": 321
     }'
```

Получить пользователя:
```
curl -X GET "http://localhost:8000/users/1" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

Обновить пользователя (может сам пользователь или админ):
```
curl -X PUT "http://localhost:8000/users/1" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "denis",
       "email": "den@gmail.ru",
       "password": "12345",
       "is_verified": true,
       "avatar": "321"
     }'
```

Удалить пользователя (может сам пользователь или админ):
```
curl -X DELETE "http://localhost:8000/users/1" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

Создать новость (может только верифицированные пользователи):
```
curl -X POST "http://localhost:8000/news/" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "news",
       "content": {"text": "something"},
       "cover": "aaa"
     }'
```

Получить новость:
```
curl -X GET "http://localhost:8000/news/1" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

Обновить новость (может только автор или админ):
```
curl -X PUT "http://localhost:8000/news/1" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "news",
       "content": {"text": "something"},
       "cover": "12345"
     }'
```

Удалить новость (может только автор или админ):
```
curl -X DELETE "http://localhost:8000/news/1" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

Создать комментарий:
```
curl -X POST "http://localhost:8000/comments/" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "news_id": 1,
       "text": "text"
     }'
```

Получить комментарий:
```
curl -X GET "http://localhost:8000/comments/1" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

Обновить комментарий (может только автор или админ):
```
curl -X PUT "http://localhost:8000/comments/1" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "news_id": 1,
       "text": "new text"
     }'
```

Удалить комментарий (может только автор или админ):
```
curl -X DELETE "http://localhost:8000/comments/1" \
     -H "Authorization: Bearer YOUR_TOKEN"
```


### Меры безопасности:
- Пароль хранится в бд в виде хеша
- Логин в базе данных уникальный
- Сырой пароль не логируется
- Пароль валидируется: требуется длина не меньше 8 символов, минимум 1 заглавная, 1 строчная, 1 цифра, 1 спецсимвол.
- Логин валидируется: требуется длина от 3 до 32 символов допустимые символы: латиница/цифры/._-