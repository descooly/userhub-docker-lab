# Лабораторная работа по Docker

## Используемый стек

- **Backend**: Flask (Python 3.11)
- **Frontend**: Nginx + HTML + JavaScript (современный тёмный дизайн)
- **База данных**: PostgreSQL 15
- **Кэш / Статистика**: Redis 7
- **Оркестрация**: Docker Compose v2

## Архитектура проекта

Browser → http://localhost:8080
↓
Nginx (frontend)
↓ proxy /api/
Flask Backend
├── PostgreSQL (persistent)
└── Redis (счётчики запросов)
text## Функциональность приложения

- Добавление нового пользователя (имя + email)
- Просмотр списка всех пользователей (сортировка по ID)
- Удаление пользователей
- Просмотр статистики запросов (через Redis)
- Health check всех сервисов
- Полная персистентность данных

## Структура проекта

```bash
userhub-docker-lab/
├── docker-compose.yml
├── .env
├── backend/
│ ├── Dockerfile
│ ├── requirements.txt
│ └── app.py
├── frontend/
│ ├── Dockerfile
│ ├── nginx.conf
│ └── index.html
├── db/
│ └── init.sql
├── README.md
└── .gitignore
```

## Как запустить проект

```bash
# 1. Клонировать репозиторий
git clone https://github.com/ВАШ_НИК/userhub-docker-lab.git
cd userhub-docker-lab

# 2. Запустить все сервисы
docker compose up --build -d

# 3. Открыть приложение в браузере
open http://localhost:8080
После запуска приложение будет доступно по адресу: http://localhost:8080
Скриншоты
```

## Демонстрация работы
![Запись экрана 2026-03-25 в 22 12 28](https://github.com/user-attachments/assets/3a307573-160b-4831-8625-49c23f89b7a1)
