import logging
import os

from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler

TELEGRAM_API_KEY = os.environ["TELEGRAM_API_KEY"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )


application = Application.builder().token(TELEGRAM_API_KEY).build()

start_handler = CommandHandler("start", start)
application.add_handler(start_handler)
