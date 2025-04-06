import asyncio
import logging
from aiogram import Bot, Dispatcher
from configs.config import TELEGRAM_BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

from bot import *

async def main():
    logger.info("Deleting webhook...")
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Starting the bot...")
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    asyncio.run(main())
