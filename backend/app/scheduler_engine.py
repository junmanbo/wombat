#!/usr/bin/env python3
"""
Scheduler Engine Service

Standalone service for running scheduled batch jobs independently from the FastAPI backend.
This service manages data collection tasks (symbols and price data) from various exchanges.
"""

import asyncio
import signal
import sys
from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.core.logging_config import get_logger

# --- Logger Setup ---
logger = get_logger(__name__)
# --- End of Logger Setup ---


# Get project root (backend directory)
PROJECT_ROOT = Path(__file__).parent.parent

# Import collection functions from scripts
sys.path.append(str(PROJECT_ROOT / "scripts"))

from scripts.collect_symbols import main as collect_symbols_main
from scripts.collect_price_data import main as collect_price_data_main


class SchedulerEngine:
    """Manages scheduled batch jobs for data collection."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=str(settings.TZ))
        self.is_shutting_down = False

    async def run_collect_symbols(self):
        """Executes the collect_symbols.py script."""
        try:
            logger.info("Starting symbol collection job...")
            await collect_symbols_main()
            logger.info("Symbol collection job completed successfully")
        except Exception:
            logger.error("Symbol collection job failed", exc_info=True)

    async def run_collect_price_data(self):
        """Executes the collect_price_data.py script."""
        try:
            logger.info("Starting price data collection job...")
            # Override sys.argv to pass default arguments
            original_argv = sys.argv
            sys.argv = ["collect_price_data.py", "--exchange", "all"]
            await collect_price_data_main()
            sys.argv = original_argv
            logger.info("Price data collection job completed successfully")
        except Exception:
            logger.error("Price data collection job failed", exc_info=True)

    def setup_jobs(self):
        """Configure scheduled jobs."""
        # Run symbol collection every day at midnight (00:00)
        self.scheduler.add_job(
            self.run_collect_symbols,
            "cron",
            hour=0,
            minute=0,
            id="collect_symbols",
            name="Collect Symbols from Exchanges",
            replace_existing=True,
        )
        logger.info("Scheduled job: Collect symbols at 00:00 daily")

        # Run price data collection every day at 00:02
        self.scheduler.add_job(
            self.run_collect_price_data,
            "cron",
            hour=0,
            minute=2,
            id="collect_price_data",
            name="Collect Price Data from Exchanges",
            replace_existing=True,
        )
        logger.info("Scheduled job: Collect price data at 00:02 daily")

    def start(self):
        """Start the scheduler engine."""
        logger.info("=" * 60)
        logger.info("Starting Scheduler Engine Service")
        logger.info(f"Timezone: {settings.TZ}")
        logger.info(f"Current time: {datetime.now()}")
        logger.info("=" * 60)

        self.setup_jobs()
        self.scheduler.start()

        logger.info("Scheduler engine started successfully")
        logger.info("Scheduled jobs:")
        for job in self.scheduler.get_jobs():
            logger.info(f"  - {job.name} (ID: {job.id}): {job.trigger}")

    def shutdown(self):
        """Shutdown the scheduler engine gracefully."""
        if self.is_shutting_down:
            return

        self.is_shutting_down = True
        logger.info("Shutting down scheduler engine...")

        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)

        logger.info("Scheduler engine shut down successfully")

    async def run_forever(self):
        """Keep the service running indefinitely."""
        try:
            # Keep the event loop running
            while not self.is_shutting_down:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Scheduler engine event loop cancelled")


def setup_signal_handlers(engine: SchedulerEngine):
    """Setup signal handlers for graceful shutdown."""

    def signal_handler(signum, _frame):
        logger.info(f"Received signal {signum}, initiating shutdown...")
        engine.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """Main entry point for the scheduler engine service."""
    engine = SchedulerEngine()

    # Setup signal handlers for graceful shutdown
    setup_signal_handlers(engine)

    try:
        # Start the scheduler
        engine.start()

        # Run forever
        await engine.run_forever()

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception:
        logger.error("Fatal error in scheduler engine", exc_info=True)
        sys.exit(1)
    finally:
        engine.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
