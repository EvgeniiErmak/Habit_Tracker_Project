# Используем базовый образ Python
FROM python:3.11

# Устанавливаем рабочую директорию в контейнере
WORKDIR /code

# Копируем зависимости в контейнер
COPY ./requirements.txt /code/

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем код приложения в контейнер
COPY . .

# Команда для запуска приложения при старте контейнера
CMD ["python", "manage.py", "runserver"]
