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
    user_id: str | None = None,
    is_demo: bool = True,
):
    """
    Collect price data from KIS (Korea Investment & Securities).

    Args:
        market: Market filter ('KOSPI', 'KOSDAQ', or None for all)
        days_back: Number of days to go back from today
        limit: Maximum number of symbols to process (None for all)
        user_id: User UUID to fetch API keys from user_api_keys table
        is_demo: Whether to use demo or production API keys (default: True)
    """
    print("Starting KIS price data collection...")

    import uuid as uuid_module

    # Convert string user_id to UUID if provided
    user_uuid = None
    if user_id:
        try:
            user_uuid = uuid_module.UUID(user_id)
            print(f"Using API keys for user: {user_uuid}")
        except ValueError:
            print(f"Error: Invalid user_id format: {user_id}")
            print("Please provide a valid UUID")
            raise

    with Session(engine) as session:
        collector = KISPriceCollector(session, user_id=user_uuid, is_demo=is_demo)
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
        "--user-id",
        type=str,
        default=None,
        help="User UUID for KIS (to fetch API keys from user_api_keys table)",
    )
    parser.add_argument(
        "--is-demo",
        action="store_true",
        default=True,
        help="Use demo/paper trading API keys for KIS (default: True)",
    )
    parser.add_argument(
        "--is-prod",
        action="store_true",
        help="Use production API keys for KIS (overrides --is-demo)",
    )

    args = parser.parse_args()

    # Handle is_demo flag
    is_demo = args.is_demo
    if args.is_prod:
        is_demo = False

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
                user_id=args.user_id,
                is_demo=is_demo,
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
