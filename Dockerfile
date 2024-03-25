# Используйте официальный образ Python как базовый
FROM python:3.11-slim

# Установите рабочую директорию в контейнере
WORKDIR /app

# Копируйте файлы проекта в контейнер
COPY . /app

# Установите poetry
RUN pip install poetry

# Отключите создание виртуального окружения в Poetry и установите зависимости
RUN poetry config virtualenvs.create false && \
    poetry export -f requirements.txt --without-hashes | pip install -r /dev/stdin

# Команда для запуска приложения
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
