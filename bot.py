import os
import json
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ===== Environment Variables =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_USERNAME = os.environ.get("BOT_USERNAME")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

MOVIE_FILE = "movies.json"
EXPIRY_TIME = 900  # 15 minutes


# ===== Helpers =====
def load_movies():
    if not os.path.exists(MOVIE_FILE):
        return {}
    with open(MOVIE_FILE, "r") as f:
        return json.load(f)


def save_movies(data):
    with open(MOVIE_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ===== Commands =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "👋 Welcome!\n\n"
            "Click a movie link from our channel to receive the movie."
        )
        return

    movie_id = context.args[0]
    movies = load_movies()

    if movie_id not in movies:
        await update.message.reply_text("❌ Movie not found or expired.")
        return

    movie = movies[movie_id]
    current_time = int(time.time())

    if current_time - movie["added_at"] > EXPIRY_TIME:
        await update.message.reply_text(
            "⏰ This movie link has expired.\nPlease check the channel for a new link."
        )
        return

    await update.message.reply_text(
        f"🎬 {movie['title']}\n\n"
        f"🔗 {movie['link']}\n\n"
        "⚠️ Save it now (expires soon)"
    )


async def addmovie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        text = " ".join(context.args)
        movie_id, title, link = [x.strip() for x in text.split("|")]

        movies = load_movies()
        movies[movie_id] = {
            "title": title,
            "link": link,
            "added_at": int(time.time())
        }

        save_movies(movies)

        deep_link = f"https://t.me/{BOT_USERNAME}?start={movie_id}"

        await update.message.reply_text(
            "✅ Movie added successfully!\n\n"
            f"🎬 {title}\n"
            f"🔗 Bot Link:\n{deep_link}"
        )

    except Exception:
        await update.message.reply_text(
            "❌ Wrong format.\n\n"
            "Use:\n"
            "/addmovie movie_id | Movie Title | movie_link"
        )


# ===== Run Bot =====
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addmovie", addmovie))

    print("Bot started...")
    app.run_polling()
