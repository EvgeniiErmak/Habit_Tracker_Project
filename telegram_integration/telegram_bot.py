# telegram_integration/telegram_bot.py
import logging
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token):
        self.bot = Bot(token)
        self.updater = Updater(bot=self.bot, use_context=True)
        self.dispatcher = self.updater.dispatcher

    def start_bot(self):
        self.dispatcher.add_handler(CommandHandler("start", self.start_handler))
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.echo_handler))
        self.dispatcher.add_error_handler(self.error_handler)
        self.updater.start_polling()
        self.updater.idle()

    def start_handler(self, update, context):
        chat_id = update.effective_chat.id
        context.bot.send_message(chat_id=chat_id, text="Bot started!")

    def echo_handler(self, update, context):
        chat_id = update.effective_chat.id
        text = update.message.text
        context.bot.send_message(chat_id=chat_id, text=f"You said: {text}")

    def error_handler(self, update, context):
        logger.error(f"Update {update} caused error {context.error}")

    def send_message(self, chat_id, text):
        try:
            self.bot.send_message(chat_id=chat_id, text=text)
            logger.info(f"Message sent to {chat_id}: {text}")
        except Exception as e:
            logger.error(f"Error sending message to {chat_id}: {str(e)}")
