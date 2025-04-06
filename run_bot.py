#!/usr/bin/env python3
"""
Script to launch the bot
"""
import os
import sys
import logging

# Add current directory to search paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Launch cheap flights bot")
    parser.add_argument("--webhook", action="store_true", help="Run via webhook instead of polling")

    args = parser.parse_args()

    if args.webhook:
        logger.info("Starting bot with webhook...")
        from management.webhook import main
        main()
    else:
        logger.info("Starting bot with polling...")
        from polling import main
        import asyncio
        asyncio.run(main())
