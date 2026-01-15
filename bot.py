import os
import json
import time
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ================= ENV =================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_USERNAME = os.environ.get("BOT_USERNAME")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

MOVIE_FILE = "movies.json"
EXPIRY_TIME = 900  # 15 minutes

# ================= FLASK (RENDER NEEDS THIS) =================
app = Flask(__name__)

@app.route("/")
def home():
    return "OK", 200

def start_flask():
    port = int(os.environ.get("PORT"))  # RENDER PROVIDED PORT
    app.run(host="0.0.0.0", port=port)

# ================= MOVIE HELPERS =================
def load_movies():
    if not os.path.exists(MOVIE_FILE):
        return {}
    with open(MOVIE_FILE, "r") as f:
        return json.load(f)

def save_movies(data):
    with open(MOVIE_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ================= BOT COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("👋 Welcome! Click a movie link.")
        return

    movie_id = context.args[0]
    movies = load_movies()

    if movie_id not in movies:
        await update.message.reply_text("❌ Movie not found or expired.")
        return

    movie = movies[movie_id]
    if int(time.time()) - movie["added_at"] > EXPIRY_TIME:
        await update.message.reply_text("⏰ Link expired.")
        return

    await update.message.reply_text(
        f"🎬 {movie['title']}\n\n🔗 {movie['link']}"
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
        await update.message.reply_text(f"✅ Movie added\n{deep_link}")

    except:
        await update.message.reply_text(
            "❌ Format:\n/addmovie id | title | link"
        )

# ================= RUN BOT =================
def run_bot():
    tg_app = ApplicationBuilder().token(BOT_TOKEN).build()
    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(CommandHandler("addmovie", addmovie))
    tg_app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=start_flask, daemon=True).start()
    run_bot()
