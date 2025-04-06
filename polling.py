import asyncio
import logging
from aiogram import Bot, Dispatcher
from configs.config import load_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

from bot import bot, dp

async def main():
    """Start the bot in polling mode"""
    logger.info("Starting bot in polling mode")

    # Delete webhook if exists
    await bot.delete_webhook(drop_pending_updates=True)

    # Start polling
    logger.info("Bot is running...")
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    asyncio.run(main())
