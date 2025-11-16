#!/usr/bin/env python3
"""
Price Data Collection Script

Collects historical price (OHLCV) data from exchanges and stores them in the database.
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import Session

from app.core.db import engine
from app.core.logging_config import get_logger
from app.engine.collectors.kis_price import KISPriceCollector
from app.engine.collectors.upbit_price import UpbitPriceCollector

# --- Logger Setup ---
logger = get_logger(__name__)
# --- End of Logger Setup ---


async def collect_upbit_prices(
    timeframe: str = "1d", days_back: int = 1, limit: int | None = None
):
    """
    Collect price data from Upbit exchange.

    Args:
        timeframe: Timeframe for candles ('1m', '5m', '1h', '1d', etc.)
        days_back: Number of days to go back from today
        limit: Maximum number of symbols to process (None for all)
    """
    logger.info("Starting Upbit price data collection...")

    with Session(engine) as session:
        collector = UpbitPriceCollector(session)
        try:
            stats = await collector.collect_all_crypto_prices(
                timeframe=timeframe, days_back=days_back, limit=limit
            )

            summary_message = (
                "Upbit price data collection completed: "
                f"Symbols processed: {stats['symbols_processed']}, "
                f"Total created: {stats['total_created']}, "
                f"Total skipped: {stats['total_skipped']}"
            )
            logger.info(summary_message)

            return stats

        except Exception:
            logger.error("Error collecting Upbit price data", exc_info=True)
            raise


def collect_kis_prices(
    market: str | None = None,
    days_back: int = 1,
    limit: int | None = None,
):
    """
    Collect price data from KIS (Korea Investment & Securities) using pykrx.

    Args:
        market: Market filter ('KOSPI', 'KOSDAQ', or None for all)
        days_back: Number of days to go back from today
        limit: Maximum number of symbols to process (None for all)
    """
    logger.info("Starting KIS price data collection (using pykrx)...")

    with Session(engine) as session:
        collector = KISPriceCollector(session)
        try:
            stats = collector.collect_all_stock_prices(
                market=market, days_back=days_back, limit=limit
            )

            summary_message = (
                "KIS price data collection completed: "
                f"Symbols processed: {stats['symbols_processed']}, "
                f"Symbols failed: {stats['symbols_failed']}, "
                f"Total created: {stats['total_created']}, "
                f"Total skipped: {stats['total_skipped']}"
            )
            logger.info(summary_message)

            return stats

        except Exception:
            logger.error("Error collecting KIS price data", exc_info=True)
            raise


async def main():
    """Main entry point for price data collection."""
    parser = argparse.ArgumentParser(
        description="Collect historical price data from exchanges"
    )
    parser.add_argument(
        "--timeframe",
        type=str,
        default="1d",
        help="Timeframe for candles (default: 1d). Options: 1m, 5m, 15m, 1h, 4h, 1d, 1w",
    )
    parser.add_argument(
        "--days-back",
        type=int,
        default=1,
        help="Number of days to go back from today (default: 1)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of symbols to process (default: None - process all)",
    )
    parser.add_argument(
        "--exchange",
        type=str,
        default="all",
        choices=["upbit", "kis", "all"],
        help="Exchange to collect from (default: all)",
    )
    parser.add_argument(
        "--market",
        type=str,
        default=None,
        choices=["KOSPI", "KOSDAQ"],
        help="Market filter for KIS (default: None - all markets)",
    )
    args = parser.parse_args()

    try:
        if args.exchange == "upbit":
            await collect_upbit_prices(
                timeframe=args.timeframe, days_back=args.days_back, limit=args.limit
            )
        elif args.exchange == "kis":
            collect_kis_prices(
                market=args.market,
                days_back=args.days_back,
                limit=args.limit,
            )
        elif args.exchange == "all":
            logger.info("--- Collecting from all exchanges: Upbit and KIS ---")
            await collect_upbit_prices(
                timeframe=args.timeframe, days_back=args.days_back, limit=args.limit
            )
            logger.info("\n" + "-" * 20 + "\n")
            collect_kis_prices(
                market=args.market,
                days_back=args.days_back,
                limit=args.limit,
            )
        else:
            logger.error(f"Exchange '{args.exchange}' not supported yet")
            sys.exit(1)

        logger.info("Price data collection completed successfully!")

    except Exception:
        logger.error("Price data collection failed", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
