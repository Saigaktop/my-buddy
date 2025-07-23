#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Buddy‑bot for Telegram ➜ Fly.io.

• health‑чек  /                                 → 200 OK  
• слушает      0.0.0.0:8080                     → проходит smoke‑check  
• PTB v20      без устаревших аргументов  
• пример tick‑джоба через APScheduler
"""

import os
import logging
from functools import partial

from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger


# ---------------------------------------------------------------------------
# ENV‑параметры
# ---------------------------------------------------------------------------
BOT_TOKEN = os.environ["BOT_TOKEN"]                         # export BOT_TOKEN=...
APP_NAME = os.getenv("FLY_APP_NAME", "my-buddy")
PORT = int(os.getenv("PORT", 8080))
PUBLIC_URL = f"https://{APP_NAME}.fly.dev"                  # адрес для Telegram

ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0")) or None  # опционально

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("buddy-bot")


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🤖 Бот запущен и готов к работе!")


async def health(_: web.Request) -> web.Response:
    return web.Response(text="ok")


async def tick(bot, *_):
    if ADMIN_CHAT_ID:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text="✅ tick()")
        logger.info("Tick sent")


# ---------------------------------------------------------------------------
# post_init ­– выполняется сразу после инициализации Application
# ---------------------------------------------------------------------------
async def post_init(app: Application) -> None:
    # 1) health‑роут
    app.web_app.router.add_get("/healthz", health)
    logger.info("Health route / зарегистрирован")

    # 2) запуск APScheduler
    sch = AsyncIOScheduler(timezone="UTC")
    sch.add_job(
        partial(tick, app.bot),
        trigger=IntervalTrigger(minutes=1),
        id="tick",
        max_instances=1,
        coalesce=True,
    )
    sch.start()
    logger.info("APScheduler запущен")


# ---------------------------------------------------------------------------
# bootstrap
# ---------------------------------------------------------------------------
def main() -> None:
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    application.add_handler(CommandHandler("start", cmd_start))

    logger.info("Запускаю run_webhook()")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        path=f"/{BOT_TOKEN}",
        webhook_url=f"{PUBLIC_URL}/{BOT_TOKEN}",
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
