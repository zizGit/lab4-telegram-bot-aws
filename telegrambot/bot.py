import io
import logging
import os

from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from nure.schedule import read_outlook_calendar_csv

TELEGRAM_API_KEY = os.environ["TELEGRAM_API_KEY"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

(
    START,
    UPLOAD,
) = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Завантажте файл з розкладом у форматі Outlook 2002/XP (*.CSV).",
    )

    return UPLOAD


async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    f = await context.bot.get_file(update.message.document.file_id)
    mem = io.BytesIO()
    await f.download_to_memory(mem)

    mem.seek(0)

    events = read_outlook_calendar_csv(io.TextIOWrapper(mem, encoding="cp1251"))

    await update.message.reply_text(f"Завантажено {len(events)} подій.")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("Bye! I hope we can talk again some day.")

    return ConversationHandler.END


application = Application.builder().token(TELEGRAM_API_KEY).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        UPLOAD: [MessageHandler(filters.Document.ALL, upload)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

application.add_handler(conv_handler)
