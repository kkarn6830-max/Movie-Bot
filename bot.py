import os
import time
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

EXPIRY_TIME = 900  # 15 minutes

MOVIES = {}  # movie_id → data


# ================= AUTO DELETE =================
async def auto_delete(bot, chat_id, message_id):
    await asyncio.sleep(EXPIRY_TIME)
    try:
        await bot.delete_message(chat_id, message_id)
    except:
        pass


# ================= ADMIN FILE ADD =================
async def admin_file_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    msg = update.message
    if not msg.caption or not msg.caption.startswith("#"):
        return

    movie_id = msg.caption.split()[0][1:]
    title = msg.caption.split("\n", 1)[1] if "\n" in msg.caption else movie_id

    if msg.video:
        file_id = msg.video.file_id
        ftype = "video"
    elif msg.document:
        file_id = msg.document.file_id
        ftype = "document"
    else:
        return

    MOVIES[movie_id] = {
        "title": title,
        "file_id": file_id,
        "type": ftype,
        "time": time.time()
    }

    bot_username = (await context.bot.get_me()).username
    deep_link = f"https://t.me/{bot_username}?start={movie_id}"

    await msg.reply_text(
        "✅ MOVIE ADDED\n\n"
        f"🎬 {title}\n\n"
        "🔗 Share this link in channel:\n"
        f"{deep_link}\n\n"
        "⚠️ Auto-deletes in 15 minutes"
    )


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "🎬 Welcome!\n\n"
            "Open a movie link from our channel."
        )
        return

    movie_id = context.args[0]
    movie = MOVIES.get(movie_id)

    if not movie:
        await update.message.reply_text(
            "⏰ This movie is no longer available.\n"
            "Check the channel for a new link."
        )
        return

    disclaimer = (
        "⚠️ IMPORTANT NOTICE\n\n"
        "This file will be AUTO-DELETED in 15 minutes.\n\n"
        "👉 Save it to *Saved Messages* now.\n"
        "👉 Do NOT share publicly.\n"
        "👉 For educational use only.\n"
    )

    await update.message.reply_text(disclaimer, parse_mode="Markdown")

    if movie["type"] == "video":
        sent = await update.message.reply_video(
            movie["file_id"],
            caption=f"🎬 {movie['title']}"
        )
    else:
        sent = await update.message.reply_document(
            movie["file_id"],
            caption=f"🎬 {movie['title']}"
        )

    asyncio.create_task(
        auto_delete(context.bot, update.effective_chat.id, sent.message_id)
    )


# ================= RUN =================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VIDEO | filters.Document.ALL, admin_file_listener))

app.run_polling()
