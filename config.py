
import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

WEBHOOK_HOST = ''
WEBHOOK_PATH = f'/webhook/{TELEGRAM_BOT_TOKEN}'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = 4040

SEARCH_PERIODS = {
    "week": 7,
    "month": 30
}
