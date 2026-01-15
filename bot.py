import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

EXPIRY_TIME = 900  # 15 minutes

MOVIES = {}  # movie_code -> {file_id, title, type}


# ---------------- AUTO DELETE ----------------
async def auto_delete(bot, chat_id, message_id):
    await asyncio.sleep(EXPIRY_TIME)
    try:
        await bot.delete_message(chat_id, message_id)
    except:
        pass


# ---------------- CHANNEL LISTENER ----------------
async def channel_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.channel_post
    if not msg or not msg.caption:
        return

    if not msg.caption.startswith("#"):
        return

    movie_code = msg.caption.split()[0][1:]
    title = msg.caption.split("\n", 1)[1] if "\n" in msg.caption else movie_code

    if msg.document:
        file_id = msg.document.file_id
        ftype = "document"
    elif msg.video:
        file_id = msg.video.file_id
        ftype = "video"
    else:
        return

    MOVIES[movie_code] = {
        "file_id": file_id,
        "title": title,
        "type": ftype
    }

    print(f"[SAVED] {movie_code} -> {title}")


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "🎬 Open a movie link from our channel."
        )
        return

    code = context.args[0]

    if code not in MOVIES:
        await update.message.reply_text(
            "⏰ This movie is no longer available."
        )
        return

    movie = MOVIES[code]

    await update.message.reply_text(
        "⚠️ IMPORTANT NOTICE\n\n"
        "This file will be auto-deleted in 15 minutes.\n"
        "Please save it to *Saved Messages*.\n",
        parse_mode="Markdown"
    )

    if movie["type"] == "document":
        sent = await update.message.reply_document(
            movie["file_id"],
            caption=f"🎬 {movie['title']}"
        )
    else:
        sent = await update.message.reply_video(
            movie["file_id"],
            caption=f"🎬 {movie['title']}"
        )

    asyncio.create_task(
        auto_delete(context.bot, update.effective_chat.id, sent.message_id)
    )


# ---------------- RUN ----------------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.Chat(CHANNEL_ID), channel_listener))
app.add_handler(CommandHandler("start", start))

app.run_polling()
