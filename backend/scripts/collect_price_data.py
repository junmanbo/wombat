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
from app.engine.collectors.kis_price import KISPriceCollector
from app.engine.collectors.upbit_price import UpbitPriceCollector


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
    print("Starting Upbit price data collection...")

    with Session(engine) as session:
        collector = UpbitPriceCollector(session)
        try:
            stats = await collector.collect_all_crypto_prices(
                timeframe=timeframe, days_back=days_back, limit=limit
            )

            print(f"\nUpbit price data collection completed:")
            print(f"  Symbols processed: {stats['symbols_processed']}")
            print(f"  Total created: {stats['total_created']}")
            print(f"  Total skipped: {stats['total_skipped']}")

            return stats

        except Exception as e:
            print(f"Error collecting Upbit price data: {e}")
            raise


def collect_kis_prices(
    market: str | None = None,
    days_back: int = 1,
    limit: int | None = None,
    env: str = "vps",
):
    """
    Collect price data from KIS (Korea Investment & Securities).

    Args:
        market: Market filter ('KOSPI', 'KOSDAQ', or None for all)
        days_back: Number of days to go back from today
        limit: Maximum number of symbols to process (None for all)
        env: Environment ('vps' for demo, 'prod' for real trading)
    """
    print("Starting KIS price data collection...")

    with Session(engine) as session:
        collector = KISPriceCollector(session, env=env)
        try:
            stats = collector.collect_all_stock_prices(
                market=market, days_back=days_back, limit=limit
            )

            print(f"\nKIS price data collection completed:")
            print(f"  Symbols processed: {stats['symbols_processed']}")
            print(f"  Symbols failed: {stats['symbols_failed']}")
            print(f"  Total created: {stats['total_created']}")
            print(f"  Total skipped: {stats['total_skipped']}")

            return stats

        except Exception as e:
            print(f"Error collecting KIS price data: {e}")
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
        default="upbit",
        choices=["upbit", "kis"],
        help="Exchange to collect from (default: upbit)",
    )
    parser.add_argument(
        "--market",
        type=str,
        default=None,
        choices=["KOSPI", "KOSDAQ"],
        help="Market filter for KIS (default: None - all markets)",
    )
    parser.add_argument(
        "--env",
        type=str,
        default="vps",
        choices=["vps", "prod"],
        help="KIS environment: vps for demo, prod for real trading (default: vps)",
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
                env=args.env,
            )
        else:
            print(f"Exchange '{args.exchange}' not supported yet")
            sys.exit(1)

        print("\nPrice data collection completed successfully!")

    except Exception as e:
        print(f"\nPrice data collection failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
