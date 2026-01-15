import os
import json
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_USERNAME = os.environ.get("BOT_USERNAME")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

def load_movies():
    with open("movies.json", "r") as f:
        return json.load(f)

def save_movies(data):
    with open("movies.json", "w") as f:
        json.dump(data, f, indent=4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("👋 Send a movie link from our channel.")
        return

    movie_id = context.args[0]
    movies = load_movies()

    if movie_id not in movies:
        await update.message.reply_text("❌ Movie not found.")
        return

    movie = movies[movie_id]
    if int(time.time()) - movie["added_at"] > 900:
        await update.message.reply_text("⏰ This movie link has expired.")
        return

    await update.message.reply_text(
        f"🎬 {movie['title']}\n\n🔗 {movie['link']}\n\n⚠️ Save it now (15 min limit)"
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
            f"✅ Movie added!\n\n🔗 Bot Link:\n{deep_link}"
        )
    except:
        await update.message.reply_text("❌ Wrong format.")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addmovie", addmovie))
app.run_polling()
Update bot config
