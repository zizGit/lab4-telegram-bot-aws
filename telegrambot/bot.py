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

from nure.db import delete_schedule, create_schedule, put_schedule, select
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
    """Downloads a file with schedule, parse it, and add to the database."""
    user_id = str(update.message.from_user.id)

    # Download.
    await update.message.reply_text("Завантажую події. Зачекайте будь ласка.")
    f = await context.bot.get_file(update.message.document.file_id)
    mem = io.BytesIO()
    await f.download_to_memory(mem)
    mem.seek(0)

    # Parse.
    events = read_outlook_calendar_csv(io.TextIOWrapper(mem, encoding="cp1251"))

    if len(events) > 0:
        # Add to the database.
        delete_schedule(user_id)
        create_schedule(user_id)
        put_schedule(user_id, events)

        # Send a message.
        await update.message.reply_text(
            f"Завантажено {len(events)} подій. Напишіть дату у форматі дд.мм.рррр, наприклад: 21.12.2023"
        )

    else:
        await update.message.reply_text(f"Події не знайдені.")

    return ConversationHandler.END


async def select_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    events = select(user_id, update.message.text.strip(" \t\n"))

    if len(events) == 0:
        await update.message.reply_text(
            f"Події на дату {update.message.text} не знайдені."
        )

    else:
        events_str = "\n".join(
            [
                f"{event.start_time} - {event.end_time}: {event.title}"
                for event in events
            ]
        )
        await update.message.reply_text(
            f"Знайдено {len(events)} подій на дату {update.message.text}:\n\n{events_str}"
        )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("До побаченя!")

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
application.add_handler(
    MessageHandler(filters.Regex(r"^\d{2}\.\d{2}\.\d{4}$"), select_request)
)
