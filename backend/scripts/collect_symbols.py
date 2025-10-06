#!/usr/bin/env python3
"""
Symbol Data Collection Script

Collects symbol data from exchanges and stores them in the database.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import Session

from app.core.db import engine
from app.engine.collectors import UpbitCollector


async def collect_upbit_symbols():
    """Collect symbols from Upbit exchange."""
    print("Starting Upbit symbol collection...")

    with Session(engine) as session:
        collector = UpbitCollector(session)
        try:
            count = await collector.collect_and_save()
            print(f"Successfully collected {count} symbols from Upbit")
            return count
        except Exception as e:
            print(f"Error collecting Upbit symbols: {e}")
            raise


async def main():
    """Main entry point for symbol collection."""
    try:
        # Collect from Upbit
        await collect_upbit_symbols()

        print("\nSymbol collection completed successfully!")

    except Exception as e:
        print(f"\nSymbol collection failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
