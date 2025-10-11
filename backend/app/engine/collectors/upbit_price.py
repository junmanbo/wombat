"""
Upbit Price Data Collector

Collects historical OHLCV (Open, High, Low, Close, Volume) price data
from Upbit exchange using ccxt.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import ccxt.async_support as ccxt
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models.exchanges import Exchange
from app.models.price_data import PriceData
from app.models.symbols import Symbol


class UpbitPriceCollector:
    """Collector for Upbit exchange price data (OHLCV)."""

    def __init__(self, session: Session):
        """
        Initialize Upbit price collector.

        Args:
            session: Database session for data persistence
        """
        self.session = session
        self.exchange_code = "upbit"
        self.exchange_id: int | None = None
        self.ccxt_exchange: ccxt.upbit | None = None

    async def _init_exchange(self) -> None:
        """Initialize ccxt exchange instance and get exchange_id from database."""
        if self.ccxt_exchange is None:
            self.ccxt_exchange = ccxt.upbit()

        if self.exchange_id is None:
            # Get exchange from database
            statement = select(Exchange).where(Exchange.code == self.exchange_code)
            exchange = self.session.exec(statement).first()

            if not exchange:
                raise ValueError(
                    f"Exchange '{self.exchange_code}' not found in database. "
                    "Please create it first."
                )

            self.exchange_id = exchange.id

    def _get_crypto_symbols(self, limit: int | None = None) -> list[Symbol]:
        """
        Get crypto symbols from database.

        Args:
            limit: Maximum number of symbols to return (None for all)

        Returns:
            List of crypto symbols
        """
        if self.exchange_id is None:
            raise ValueError("Exchange not initialized")

        statement = (
            select(Symbol)
            .where(
                Symbol.exchange_id == self.exchange_id,
                Symbol.symbol_type == "CRYPTO",
                Symbol.is_active == True,
            )
            .order_by(Symbol.id)
        )

        if limit:
            statement = statement.limit(limit)

        return list(self.session.exec(statement).all())

    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1d",
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[list[Any]]:
        """
        Fetch OHLCV data from Upbit.

        Args:
            symbol: Trading pair symbol (e.g., "BTC/KRW")
            timeframe: Timeframe for candles ('1m', '5m', '1h', '1d', etc.)
            since: Start time for fetching data
            limit: Maximum number of candles to fetch (default: 100, max: 200)

        Returns:
            List of OHLCV data: [[timestamp, open, high, low, close, volume], ...]
        """
        await self._init_exchange()

        if not self.ccxt_exchange:
            raise RuntimeError("Exchange not initialized")

        try:
            # Convert datetime to milliseconds timestamp
            since_ms = None
            if since:
                since_ms = int(since.timestamp() * 1000)

            # Fetch OHLCV data
            ohlcv = await self.ccxt_exchange.fetch_ohlcv(
                symbol, timeframe=timeframe, since=since_ms, limit=limit
            )

            return ohlcv

        except Exception as e:
            print(f"Error fetching OHLCV for {symbol}: {e}")
            return []

    def _convert_ohlcv_to_price_data(
        self, symbol_id: int, timeframe: str, ohlcv_list: list[list[Any]]
    ) -> list[dict[str, Any]]:
        """
        Convert OHLCV data from ccxt format to PriceData format.

        Args:
            symbol_id: Database symbol ID
            timeframe: Timeframe string
            ohlcv_list: List of OHLCV data from ccxt
                       Format: [[timestamp_ms, open, high, low, close, volume], ...]

        Returns:
            List of price data dictionaries ready for database insertion
        """
        price_data_list = []

        for ohlcv in ohlcv_list:
            timestamp_ms, open_price, high_price, low_price, close_price, volume = (
                ohlcv
            )

            # Convert timestamp from milliseconds to datetime
            timestamp = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)

            # Calculate quote volume (for KRW pairs, this is the total trading amount in KRW)
            # quote_volume = volume * average_price (approximation)
            avg_price = (high_price + low_price) / 2
            quote_volume = volume * avg_price if volume and avg_price else 0

            price_data = {
                "symbol_id": symbol_id,
                "timestamp": timestamp,
                "open_price": Decimal(str(open_price)),
                "high_price": Decimal(str(high_price)),
                "low_price": Decimal(str(low_price)),
                "close_price": Decimal(str(close_price)),
                "volume": Decimal(str(volume)),
                "quote_volume": Decimal(str(quote_volume)),
                "timeframe": timeframe,
            }

            price_data_list.append(price_data)

        return price_data_list

    async def save_price_data(
        self, symbol_id: int, price_data_list: list[dict[str, Any]]
    ) -> tuple[int, int]:
        """
        Save price data to database.

        Args:
            symbol_id: Database symbol ID
            price_data_list: List of price data dictionaries

        Returns:
            Tuple of (created_count, skipped_count)
        """
        created_count = 0
        skipped_count = 0

        for price_data in price_data_list:
            try:
                # Check if price data already exists
                statement = select(PriceData).where(
                    PriceData.symbol_id == price_data["symbol_id"],
                    PriceData.timestamp == price_data["timestamp"],
                    PriceData.timeframe == price_data["timeframe"],
                )
                existing = self.session.exec(statement).first()

                if existing:
                    skipped_count += 1
                    continue

                # Create new price data
                price_data_obj = PriceData(**price_data)
                self.session.add(price_data_obj)
                created_count += 1

            except IntegrityError as e:
                self.session.rollback()
                print(f"Error saving price data for symbol_id {symbol_id}: {e}")
                skipped_count += 1
                continue

        # Commit all at once for better performance
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"Error committing price data: {e}")
            return (0, len(price_data_list))

        return (created_count, skipped_count)

    async def collect_symbol_price_data(
        self,
        symbol: Symbol,
        timeframe: str = "1d",
        days_back: int = 1,
    ) -> tuple[int, int]:
        """
        Collect price data for a single symbol.

        Args:
            symbol: Symbol object from database
            timeframe: Timeframe for candles ('1d', '1h', etc.)
            days_back: Number of days to go back from today

        Returns:
            Tuple of (created_count, skipped_count)
        """
        # Calculate since timestamp (days_back days ago)
        since = datetime.now(timezone.utc) - timedelta(days=days_back)

        print(f"Fetching {timeframe} data for {symbol.symbol} (ID: {symbol.id})...")

        # Fetch OHLCV data
        ohlcv_list = await self.fetch_ohlcv(
            symbol=symbol.symbol, timeframe=timeframe, since=since, limit=200
        )

        if not ohlcv_list:
            print(f"  No data fetched for {symbol.symbol}")
            return (0, 0)

        # Convert to price data format
        price_data_list = self._convert_ohlcv_to_price_data(
            symbol_id=symbol.id, timeframe=timeframe, ohlcv_list=ohlcv_list
        )

        # Save to database
        created, skipped = await self.save_price_data(symbol.id, price_data_list)

        print(f"  {symbol.symbol}: {created} created, {skipped} skipped")

        return (created, skipped)

    async def collect_all_crypto_prices(
        self,
        timeframe: str = "1d",
        days_back: int = 1,
        limit: int | None = None,
    ) -> dict[str, int]:
        """
        Collect price data for all crypto symbols.

        Args:
            timeframe: Timeframe for candles ('1d', '1h', etc.)
            days_back: Number of days to go back from today
            limit: Maximum number of symbols to process (None for all)

        Returns:
            Dictionary with statistics: {
                'symbols_processed': int,
                'total_created': int,
                'total_skipped': int,
            }
        """
        await self._init_exchange()

        # Get crypto symbols
        symbols = self._get_crypto_symbols(limit=limit)

        print(f"\nStarting price data collection for {len(symbols)} symbols...")
        print(f"Timeframe: {timeframe}, Days back: {days_back}\n")

        total_created = 0
        total_skipped = 0
        symbols_processed = 0

        try:
            for symbol in symbols:
                try:
                    created, skipped = await self.collect_symbol_price_data(
                        symbol=symbol, timeframe=timeframe, days_back=days_back
                    )

                    total_created += created
                    total_skipped += skipped
                    symbols_processed += 1

                except Exception as e:
                    print(f"  Error processing {symbol.symbol}: {e}")
                    continue

            print(f"\n{'='*60}")
            print(f"Collection completed!")
            print(f"Symbols processed: {symbols_processed}/{len(symbols)}")
            print(f"Total created: {total_created}")
            print(f"Total skipped: {total_skipped}")
            print(f"{'='*60}\n")

            return {
                "symbols_processed": symbols_processed,
                "total_created": total_created,
                "total_skipped": total_skipped,
            }

        finally:
            # Clean up
            if self.ccxt_exchange:
                await self.ccxt_exchange.close()
                self.ccxt_exchange = None
