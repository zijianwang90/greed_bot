#!/usr/bin/env python3
"""
Alternative bot runner that handles event loops more carefully
"""

import asyncio
import sys
from main import main, logger

def run_bot():
    """Run the bot with proper event loop handling"""
    try:
        # Check if there's already a running event loop
        loop = asyncio.get_running_loop()
        logger.info("Found existing event loop, using it directly")
        # If we're here, we're in an environment with an existing loop
        # (like Jupyter or some IDEs)
        asyncio.create_task(main())
    except RuntimeError:
        # No running event loop, create one
        logger.info("No existing event loop, creating new one")
        asyncio.run(main())

if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1) 