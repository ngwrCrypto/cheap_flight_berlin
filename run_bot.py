#!/usr/bin/env python3
"""
Скрипт для запуску бота
"""
import os
import sys
import logging

# Додаємо поточну директорію до шляхів пошуку
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Запуск бота дешевих рейсів")
    parser.add_argument("--webhook", action="store_true", help="Запустити через webhook замість polling")

    args = parser.parse_args()

    if args.webhook:
        logger.info("Запуск бота через webhook...")
        from management.webhook import main
        main()
    else:
        logger.info("Запуск бота через polling...")
        from polling import main
        import asyncio
        asyncio.run(main())
