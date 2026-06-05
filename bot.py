import asyncio
import logging
import os
import sys

import httpx
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

API_BASE = "https://top-newfilms.onrender.com/api"
FILMS_URL = f"{API_BASE}/films/"
CATEGORIES_URL = f"{API_BASE}/categories/"

BTN_ALL_FILMS = "🎬 Barcha kinolar"
BTN_CATEGORIES = "📁 Kategoriyalar"

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [[BTN_ALL_FILMS, BTN_CATEGORIES]],
    resize_keyboard=True,
)


async def fetch_json(url: str) -> list | dict:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


async def get_films() -> list[dict]:
    data = await fetch_json(FILMS_URL)
    return data if isinstance(data, list) else data.get("results", data)


async def get_categories() -> list[dict]:
    data = await fetch_json(CATEGORIES_URL)
    return data if isinstance(data, list) else data.get("results", data)


def build_films_keyboard(films: list[dict]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(film["title"], callback_data=f"film:{film['id']}")]
        for film in films
    ]
    return InlineKeyboardMarkup(buttons)


def format_film_caption(film: dict) -> str:
    category_name = film.get("category", {}).get("name", "Noma'lum")
    return (
        f"🎬 <b>{film['title']}</b> ({film['year']})\n"
        f"⭐ Reyting: {film['rating']}\n"
        f"🌍 Davlat: {film['country']}\n"
        f"🕒 Davomiyligi: {film['duration']} daqiqa\n"
        f"👨‍💼 Rejissyor: {film['director']}\n"
        f"📁 Kategoriya: {category_name}\n"
        f"📜 Tavsif: {film['description']}\n"
        f"<b>✨ {film['highlight']}</b>"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Assalomu alaykum! Kino botiga xush kelibsiz.\n"
        "Quyidagi tugmalardan birini tanlang:",
        reply_markup=MAIN_KEYBOARD,
    )


async def show_all_films(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        films = await get_films()
        await update.message.reply_text(
            "Bizdagi mavjud kinolar ro'yxati:",
            reply_markup=build_films_keyboard(films),
        )
    except httpx.HTTPError:
        logger.exception("Films API xatosi")
        await update.message.reply_text(
            "Kinolar ro'yxatini yuklab bo'lmadi. Birozdan keyin qayta urinib ko'ring."
        )


async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        categories = await get_categories()
        buttons = [
            [
                InlineKeyboardButton(
                    f"{cat['name']} ({cat['films_count']})",
                    callback_data=f"cat:{cat['id']}",
                )
            ]
            for cat in categories
        ]
        await update.message.reply_text(
            "Kategoriyalardan birini tanlang:",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    except httpx.HTTPError:
        logger.exception("Categories API xatosi")
        await update.message.reply_text(
            "Kategoriyalarni yuklab bo'lmadi. Birozdan keyin qayta urinib ko'ring."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text

    if text == BTN_ALL_FILMS:
        await show_all_films(update, context)
    elif text == BTN_CATEGORIES:
        await show_categories(update, context)
    else:
        await update.message.reply_text(
            "Iltimos, quyidagi tugmalardan foydalaning:",
            reply_markup=MAIN_KEYBOARD,
        )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data:
        return

    try:
        if data.startswith("film:"):
            film_id = int(data.split(":")[1])
            films = await get_films()
            film = next((f for f in films if f["id"] == film_id), None)

            if not film:
                await query.message.reply_text("Kino topilmadi.")
                return

            await query.message.reply_photo(
                photo=film["poster_url"],
                caption=format_film_caption(film),
                parse_mode="HTML",
            )

        elif data.startswith("cat:"):
            category_id = int(data.split(":")[1])
            films = await get_films()
            filtered = [f for f in films if f.get("category", {}).get("id") == category_id]

            if not filtered:
                await query.message.reply_text("Ushbu kategoriyada kinolar topilmadi.")
                return

            await query.message.reply_text(
                "Ushbu kategoriyadagi kinolar:",
                reply_markup=build_films_keyboard(filtered),
            )

    except httpx.HTTPError:
        logger.exception("API xatosi")
        await query.message.reply_text(
            "Ma'lumotlarni yuklab bo'lmadi. Birozdan keyin qayta urinib ko'ring."
        )
    except (ValueError, KeyError):
        logger.exception("Noto'g'ri ma'lumot")
        await query.message.reply_text("Xatolik yuz berdi. Qayta urinib ko'ring.")


def main() -> None:
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.set_event_loop(asyncio.new_event_loop())

    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("BOT_TOKEN muhit o'zgaruvchisi topilmadi. .env faylini tekshiring.")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))

    logger.info("Bot ishga tushmoqda...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
