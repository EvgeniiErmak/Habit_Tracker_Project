# telegram_integration/telegram_bot.py
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
from telegram import Bot
import logging

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token):
        self.bot = Bot(token)
        self.updater = Updater(bot=self.bot, use_context=True)
        self.dispatcher = self.updater.dispatcher

    def start_bot(self):
        self.dispatcher.add_handler(CommandHandler("start", self.start_handler))
        self.dispatcher.add_handler(CommandHandler("help", self.help_handler))
        self.dispatcher.add_handler(CommandHandler("habits", self.habits_handler))
        self.dispatcher.add_handler(CommandHandler("add_habit", self.add_habit_handler))
        self.dispatcher.add_handler(
            MessageHandler(Filters.text & ~Filters.command, self.echo_handler)
        )
        self.dispatcher.add_error_handler(self.error_handler)
        self.updater.start_polling()
        self.updater.idle()

    def start_handler(self, update, context):
        chat_id = update.effective_chat.id
        context.bot.send_message(chat_id=chat_id, text="Bot started!")

    def help_handler(self, update, context):
        chat_id = update.effective_chat.id
        context.bot.send_message(
            chat_id=chat_id,
            text="List of available commands:\n"
            "/start - Start using the application\n"
            "/help - Show list of help commands\n"
            "/habits - Show list of habits\n"
            "/add_habit - Add a new habit",
        )

    def habits_handler(self, update, context):
        chat_id = update.effective_chat.id
        # Add logic to display the list of habits to the user
        context.bot.send_message(
            chat_id=chat_id, text="List of your habits:\n1. Habit 1\n2. Habit 2"
        )

    def add_habit_handler(self, update, context):
        chat_id = update.effective_chat.id
        # Add logic to add a new habit for the user
        context.bot.send_message(
            chat_id=chat_id, text="Enter the name of the new habit"
        )

    # Новый метод для обработки команды /echo
    def echo_handler(self, update, context):
        chat_id = update.effective_chat.id
        text = update.message.text
        context.bot.send_message(chat_id=chat_id, text=f"You said: {text}")

    # Новый метод для обработки команды /echo
    def echo_command(self, update, context):
        chat_id = update.effective_chat.id
        context.bot.send_message(chat_id=chat_id, text="This is an echo command!")

    def error_handler(self, update, context):
        logger.error(f"Update {update} caused error {context.error}")

    def send_message(self, chat_id, text):
        try:
            self.bot.send_message(chat_id=chat_id, text=text)
            logger.info(f"Message sent to {chat_id}: {text}")
        except Exception as e:
            logger.error(f"Error sending message to {chat_id}: {str(e)}")


def run_telegram_bot():
    bot_token = "6508959358:AAESl7Sb20VbkYx26qU-T0piY0UF_EeiWf8"
    telegram_bot = TelegramBot(bot_token)
    telegram_bot.start_bot()


if __name__ == "__main__":
    run_telegram_bot()
