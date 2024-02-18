# telegram_integration/telegram_bot.py
import logging
from telegram import Bot

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token):
        self.bot = Bot(token)

    def send_message(self, chat_id, text):
        try:
            self.bot.send_message(chat_id=chat_id, text=text)
            logger.info(f"Message sent to {chat_id}: {text}")
        except Exception as e:
            logger.error(f"Error sending message to {chat_id}: {str(e)}")
