import logging
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from configs.config import TELEGRAM_BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

import sys
import os
# Add parent directory to import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bot import *

app = FastAPI(title="Telegram Bot Webhook")

async def on_startup():
    logger.info("Deleting old webhook...")
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info(f"Setting webhook at {WEBHOOK_URL}{WEBHOOK_PATH}")
    await bot.set_webhook(
        url=f"{WEBHOOK_URL}{WEBHOOK_PATH}",
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"]
    )

async def on_shutdown():
    logger.info("Shutting down the bot...")
    await bot.delete_webhook()
    await bot.session.close()

@app.post(WEBHOOK_PATH)
async def bot_webhook(request: Request):
    try:
        update = types.Update(**await request.json())
        await dp.feed_update(bot=bot, update=update)
        return {'ok': True}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {'ok': False, 'error': str(e)}

@app.get("/")
async def root():
    return {
        "status": "Bot is running",
        "webhook_url": f"{WEBHOOK_URL}{WEBHOOK_PATH}",
        "bot_info": await bot.get_me()
    }

@app.on_event("startup")
async def startup_event():
    await on_startup()

@app.on_event("shutdown")
async def shutdown_event():
    await on_shutdown()

def main():
    """Function to launch the webhook server"""
    import uvicorn
    logger.info(f"Starting webhook server on {WEBAPP_HOST}:{WEBAPP_PORT}")
    uvicorn.run(
        app,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
        log_level="info"
    )

if __name__ == "__main__":
    main()
