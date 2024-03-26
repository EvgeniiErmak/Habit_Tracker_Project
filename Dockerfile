# Dockerfile

# Используем базовый образ Python 3.11
FROM python:3.11-slim AS poetry-base

# Устанавливаем Poetry
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry/venv
ENV POETRY_VERSION=1.3.2
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install --upgrade pip \
    && $POETRY_VENV/bin/pip install poetry==$POETRY_VERSION

# Создаем новый этап для установки зависимостей
FROM poetry-base AS poetry-install
WORKDIR /app
COPY pyproject.toml poetry.lock* ./

# Обновляем Poetry и создаем новый файл poetry.lock
RUN /opt/poetry/venv/bin/poetry self update
RUN /opt/poetry/venv/bin/poetry lock

# Устанавливаем зависимости
RUN /opt/poetry/venv/bin/poetry install --no-root

# Создаем финальный этап для приложения
FROM python:3.11-slim AS app
COPY --from=poetry-install /opt/poetry/venv /opt/poetry/venv
ENV PATH="${PATH}:/opt/poetry/venv/bin"
WORKDIR /app
COPY . /app

# Устанавливаем зависимости
RUN /opt/poetry/venv/bin/poetry install --no-interaction --no-ansi --only=main

# Открываем порт для приложения
EXPOSE 8000

# Команда для запуска приложения Django
CMD ["/opt/poetry/venv/bin/poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
