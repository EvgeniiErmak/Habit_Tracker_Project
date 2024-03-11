# Описание проекта

Проект представляет собой приложение "Habit Tracker", которое позволяет пользователям отслеживать и управлять своими привычками. Пользователи могут добавлять новые привычки, устанавливать цели, получать напоминания и отслеживать свой прогресс.

## Основные функции

- **Добавление привычек**: Пользователи могут добавлять новые привычки с указанием названия, места, времени выполнения, действия, частоты выполнения, вознаграждения и других параметров.
- **Просмотр списка привычек**: Пользователи могут просматривать список своих привычек.
- **Получение напоминаний**: Пользователи получают уведомления о выполнении привычек в указанное время.
- **Управление привычками**: Пользователи могут редактировать, удалять и отслеживать свой прогресс в выполнении привычек.
- **Аутентификация и авторизация**: Пользователи могут регистрироваться, входить в систему и получать доступ к своему аккаунту.

## Технологии

Проект использует следующие технологии и инструменты:

- **Django**: Веб-фреймворк для разработки серверной части приложения.
- **Django REST Framework**: Библиотека Django для создания веб-интерфейса API.
- **Telegram Bot API**: API для разработки ботов для мессенджера Telegram.
- **REST API**: Взаимодействие с приложением осуществляется через RESTful API.
- **JWT (JSON Web Tokens)**: Механизм аутентификации и авторизации пользователей.
- **Python Requests**: Библиотека Python для отправки HTTP-запросов.
- **PostgreSQL**: Реляционная база данных для хранения данных приложения.

## Установка и запуск

Для установки и запуска проекта выполните следующие шаги:

1. Клонирование репозитория:

   ```bash
   git clone <ссылка_на_репозиторий>
   ```

2. Установка зависимостей:

   ```bash
   pip install -r requirements.txt
   ```

3. Настройка базы данных:

   Создайте базу данных PostgreSQL и укажите соответствующие параметры в файле `config/settings.py`.

4. Применение миграций:

   ```bash
   python manage.py migrate
   ```

5. Запуск сервера:

   ```bash
   python manage.py runserver
   ```

6. Запуск бота:

   ```bash
   python telegram_integration/views.py
   ```

Теперь вы можете открыть приложение в веб-браузере и начать использовать его!

## Контакты

Если у вас возникли вопросы или предложения по проекту, свяжитесь с нами:

- Email: djermak3000@mail.ru
- Telegram: https://t.me/DJErmak3000

## Лицензия

Этот проект лицензируется в соответствии с условиями лицензии MIT. См. файл `LICENSE` для получения дополнительной информации.