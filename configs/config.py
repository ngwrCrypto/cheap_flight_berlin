import os
from dataclasses import dataclass
from typing import Optional, Dict
from dotenv import load_dotenv

@dataclass
class TelegramConfig:
    token: str

@dataclass
class WebhookConfig:
    host: str
    path: str
    url: str
    webapp_host: str
    webapp_port: int

@dataclass
class Config:
    telegram: TelegramConfig
    webhook: WebhookConfig

# Словник періодів пошуку
SEARCH_PERIODS = {
    "week": 7,
    "month": 30
}

def load_config() -> Config:
    """Load configuration from environment variables"""
    # Load environment variables from .env file
    load_dotenv()

    # Get Telegram token
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

    # Create webhook config
    webhook_host = os.getenv('WEBHOOK_HOST', '')
    webhook_path = f'/webhook/{token}'
    webhook_url = f"{webhook_host}{webhook_path}"
    webapp_host = os.getenv('WEBAPP_HOST', '0.0.0.0')
    webapp_port = int(os.getenv('WEBAPP_PORT', '4040'))

    # Create and return config object
    return Config(
        telegram=TelegramConfig(token=token),
        webhook=WebhookConfig(
            host=webhook_host,
            path=webhook_path,
            url=webhook_url,
            webapp_host=webapp_host,
            webapp_port=webapp_port
        )
    )
