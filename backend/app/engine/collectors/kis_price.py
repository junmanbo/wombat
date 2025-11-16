"""
KIS (Korea Investment & Securities) Price Data Collector

Collects historical OHLCV (Open, High, Low, Close, Volume) price data
for Korean stocks using pykrx (Korea Exchange data crawler).
"""

import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import pandas as pd
from pykrx import stock
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models.exchanges import Exchange
from app.models.price_data import PriceData
from app.models.symbols import Symbol


class KISPriceCollector:
    """Collector for KIS (Korea Investment & Securities) stock price data."""

    def __init__(self, session: Session):
        """
        Initialize KIS price collector using pykrx.

        Args:
            session: Database session for data persistence
        """
        self.session = session
        self.exchange_code = "kis"
        self.exchange_id: int | None = None
        print("✓ KIS Price Collector initialized (using pykrx - no API authentication required)")

    def _init_exchange(self) -> None:
        """Get exchange_id from database."""
        if self.exchange_id is None:
            statement = select(Exchange).where(Exchange.code == self.exchange_code)
            exchange = self.session.exec(statement).first()

            if not exchange:
                raise ValueError(
                    f"Exchange '{self.exchange_code}' not found in database. "
                    "Please create it first."
                )

            self.exchange_id = exchange.id

    def _get_stock_symbols(
        self, market: str | None = None, limit: int | None = None
    ) -> list[Symbol]:
        """
        Get stock symbols from database.

        Args:
            market: Market filter ('KOSPI', 'KOSDAQ', or None for all)
            limit: Maximum number of symbols to return (None for all)

        Returns:
            List of stock symbols (excludes funds and ETFs with non-numeric codes)
        """
        if self.exchange_id is None:
            self._init_exchange()

        statement = select(Symbol).where(
            Symbol.exchange_id == self.exchange_id,
            Symbol.symbol_type == "STOCK",
            Symbol.is_active,
            # Filter for 6-digit numeric stock codes (excludes funds like F70100009)
            Symbol.symbol.regexp_match(r"^\d{6}$"),
        )

        if market:
            statement = statement.where(Symbol.market == market)

        statement = statement.order_by(Symbol.symbol)

        if limit:
            statement = statement.limit(limit)

        return list(self.session.exec(statement).all())

    def fetch_daily_price(
        self,
        symbol_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        """
        Fetch daily price data using pykrx.

        Args:
            symbol_code: Stock code (e.g., "005930" for Samsung)
            start_date: Start date in YYYYMMDD format (default: 30 days ago)
            end_date: End date in YYYYMMDD format (default: today)

        Returns:
            DataFrame with OHLCV data (columns: 시가, 고가, 저가, 종가, 거래량)
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

        try:
            # pykrx의 get_market_ohlcv 사용
            df = stock.get_market_ohlcv(start_date, end_date, symbol_code)

            if df.empty:
                print(f"  No data available for {symbol_code}")
                return pd.DataFrame()

            # Reset index to get 날짜 as column
            df = df.reset_index()
            return df

        except Exception as e:
            print(f"  Error fetching data for {symbol_code}: {e}")
            return pd.DataFrame()

    def _convert_pykrx_data_to_price_data(
        self, symbol_id: int, df: pd.DataFrame
    ) -> list[dict[str, Any]]:
        """
        Convert pykrx data to PriceData format.

        Args:
            symbol_id: Database symbol ID
            df: DataFrame from pykrx (columns: 날짜, 시가, 고가, 저가, 종가, 거래량)

        Returns:
            List of price data dictionaries
        """
        price_data_list = []

        for _, row in df.iterrows():
            try:
                # pykrx returns date as '날짜' column after reset_index()
                if "날짜" not in row.index:
                    print(f"  Warning: '날짜' column not found. Available columns: {list(row.index)}")
                    continue

                date_value = row["날짜"]

                # Convert date to timestamp
                if isinstance(date_value, str):
                    timestamp = datetime.strptime(date_value, "%Y%m%d").replace(
                        tzinfo=timezone.utc
                    )
                else:
                    # Already a datetime object (pandas Timestamp)
                    timestamp = pd.to_datetime(date_value).replace(tzinfo=timezone.utc)

                # pykrx column names: 시가, 고가, 저가, 종가, 거래량
                open_price = row["시가"]
                high_price = row["고가"]
                low_price = row["저가"]
                close_price = row["종가"]
                volume = row["거래량"]

                # Validate data
                if pd.isna(open_price) or pd.isna(high_price) or pd.isna(low_price) or pd.isna(close_price):
                    print(f"  Skipping row with NaN values: {date_value}")
                    continue

                if not all([open_price > 0, high_price > 0, low_price > 0, close_price > 0]):
                    print(f"  Skipping row with zero/negative values: {date_value}")
                    continue

                price_data = {
                    "symbol_id": symbol_id,
                    "timestamp": timestamp,
                    "open_price": Decimal(str(int(open_price))),
                    "high_price": Decimal(str(int(high_price))),
                    "low_price": Decimal(str(int(low_price))),
                    "close_price": Decimal(str(int(close_price))),
                    "volume": Decimal(str(int(volume))),
                    "quote_volume": Decimal("0"),  # pykrx doesn't provide quote_volume
                    "timeframe": "1d",
                }

                price_data_list.append(price_data)

            except (ValueError, KeyError) as e:
                print(f"  Error converting row: {e}")
                print(f"  Row data: {row.to_dict()}")
                continue
            except Exception as e:
                print(f"  Unexpected error converting row: {e}")
                print(f"  Row data: {row.to_dict()}")
                continue

        return price_data_list

    def save_price_data(
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
                statement = select(PriceData).where(
                    PriceData.symbol_id == price_data["symbol_id"],
                    PriceData.timestamp == price_data["timestamp"],
                    PriceData.timeframe == price_data["timeframe"],
                )
                existing = self.session.exec(statement).first()

                if existing:
                    skipped_count += 1
                    continue

                price_data_obj = PriceData(**price_data)
                self.session.add(price_data_obj)
                created_count += 1

            except IntegrityError as e:
                self.session.rollback()
                print(f"  Error saving price data for symbol_id {symbol_id}: {e}")
                skipped_count += 1
                continue

        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"  Error committing price data: {e}")
            return (0, len(price_data_list))

        return (created_count, skipped_count)

    def collect_symbol_price_data(
        self, symbol: Symbol, days_back: int = 1
    ) -> tuple[int, int]:
        """
        Collect price data for a single symbol.

        Args:
            symbol: Symbol object from database
            days_back: Number of days to go back from today

        Returns:
            Tuple of (created_count, skipped_count)
        """
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")

        print(
            f"Fetching daily data for {symbol.base_asset} ({symbol.symbol}, ID: {symbol.id})..."
        )

        df = self.fetch_daily_price(
            symbol_code=symbol.symbol, start_date=start_date, end_date=end_date
        )

        if df.empty:
            print(f"  No data fetched for {symbol.symbol}")
            return (0, 0)

        price_data_list = self._convert_pykrx_data_to_price_data(
            symbol_id=symbol.id, df=df
        )

        if not price_data_list:
            print(f"  No valid data for {symbol.symbol}")
            return (0, 0)

        created, skipped = self.save_price_data(symbol.id, price_data_list)

        print(
            f"  {symbol.base_asset} ({symbol.symbol}): {created} created, {skipped} skipped"
        )

        # No need for sleep with pykrx (no API rate limiting)

        return (created, skipped)

    def collect_all_stock_prices(
        self,
        market: str | None = None,
        days_back: int = 1,
        limit: int | None = None,
    ) -> dict[str, int]:
        """
        Collect price data for all stock symbols.

        Args:
            market: Market filter ('KOSPI', 'KOSDAQ', or None for all)
            days_back: Number of days to go back from today
            limit: Maximum number of symbols to process (None for all)

        Returns:
            Dictionary with statistics
        """
        self._init_exchange()

        symbols = self._get_stock_symbols(market=market, limit=limit)

        market_str = market if market else "ALL"
        print(
            f"\nStarting price data collection for {len(symbols)} {market_str} symbols..."
        )
        print(f"Days back: {days_back}\n")

        total_created = 0
        total_skipped = 0
        symbols_processed = 0
        symbols_failed = 0

        for symbol in symbols:
            try:
                created, skipped = self.collect_symbol_price_data(
                    symbol=symbol, days_back=days_back
                )

                total_created += created
                total_skipped += skipped
                symbols_processed += 1

            except Exception as e:
                print(f"  Error processing {symbol.symbol}: {e}")
                symbols_failed += 1
                continue

        print(f"\n{'='*60}")
        print("Collection completed!")
        print(f"Symbols processed: {symbols_processed}/{len(symbols)}")
        print(f"Symbols failed: {symbols_failed}")
        print(f"Total created: {total_created}")
        print(f"Total skipped: {total_skipped}")
        print(f"{'='*60}\n")

        return {
            "symbols_processed": symbols_processed,
            "symbols_failed": symbols_failed,
            "total_created": total_created,
            "total_skipped": total_skipped,
        }
