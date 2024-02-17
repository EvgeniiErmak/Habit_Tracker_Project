# telegram_integration/telegram_bot.py
from telegram import Bot


class TelegramBot:
    def __init__(self, token):
        self.bot = Bot(token)

    def send_message(self, chat_id, message):
        self.bot.send_message(chat_id=chat_id, text=message)

# Пример использования
# bot = TelegramBot('your_telegram_bot_token')
# bot.send_message(chat_id='your_chat_id', message='Hello, World!')
