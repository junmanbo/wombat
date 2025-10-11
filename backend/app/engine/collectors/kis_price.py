"""
KIS (Korea Investment & Securities) Price Data Collector

Collects historical OHLCV (Open, High, Low, Close, Volume) price data
for Korean stocks using KIS API.
"""

import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

# Add external open-trading-api path
# Navigate from app/engine/collectors -> app -> backend -> external
external_path = Path(__file__).parent.parent.parent.parent / "external" / "open-trading-api" / "examples_llm"
if str(external_path) not in sys.path:
    sys.path.insert(0, str(external_path))

try:
    import kis_auth as ka
except ImportError as e:
    print(f"Warning: Could not import kis_auth: {e}")
    print(f"Attempted import from: {external_path}")
    print("Please ensure KIS API configuration is set up correctly.")
    ka = None

from app.models.exchanges import Exchange
from app.models.price_data import PriceData
from app.models.symbols import Symbol


class KISPriceCollector:
    """Collector for KIS (Korea Investment & Securities) stock price data."""

    def __init__(self, session: Session, env: str = "vps"):
        """
        Initialize KIS price collector.

        Args:
            session: Database session for data persistence
            env: Environment ('vps' for demo, 'prod' for real trading)
        """
        self.session = session
        self.exchange_code = "kis"
        self.exchange_id: int | None = None
        self.env = env  # 'vps' for demo, 'prod' for production

        # Initialize KIS authentication
        if ka is None:
            raise ImportError(
                "kis_auth module not available. "
                "Please ensure open-trading-api is properly set up."
            )

        try:
            ka.auth(svr=env)
            print(f"KIS API authenticated ({env} mode)")
        except Exception as e:
            print(f"Warning: KIS API authentication failed: {e}")
            print("Price data collection may fail. Please check your KIS configuration.")

    def _init_exchange(self) -> None:
        """Get exchange_id from database."""
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

    def _get_stock_symbols(
        self, market: str | None = None, limit: int | None = None
    ) -> list[Symbol]:
        """
        Get stock symbols from database.

        Args:
            market: Market filter ('KOSPI', 'KOSDAQ', or None for all)
            limit: Maximum number of symbols to return (None for all)

        Returns:
            List of stock symbols
        """
        if self.exchange_id is None:
            self._init_exchange()

        statement = select(Symbol).where(
            Symbol.exchange_id == self.exchange_id,
            Symbol.symbol_type == "STOCK",
            Symbol.is_active == True,
        )

        if market:
            statement = statement.where(Symbol.market == market)

        statement = statement.order_by(Symbol.id)

        if limit:
            statement = statement.limit(limit)

        return list(self.session.exec(statement).all())

    def fetch_daily_price(
        self, symbol_code: str, start_date: str | None = None, end_date: str | None = None
    ) -> pd.DataFrame:
        """
        Fetch daily price data from KIS API.

        Args:
            symbol_code: Stock code (e.g., "005930" for Samsung)
            start_date: Start date in YYYYMMDD format (default: 30 days ago)
            end_date: End date in YYYYMMDD format (default: today)

        Returns:
            DataFrame with OHLCV data
        """
        # 기본 날짜 설정
        if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

        # KIS API 파라미터 설정
        # 주식현재가 일자별 API 사용
        api_url = "/uapi/domestic-stock/v1/quotations/inquire-daily-price"

        # TR_ID 설정
        if self.env == "vps":
            tr_id = "FHKST01010400"  # 모의투자
        else:
            tr_id = "FHKST01010400"  # 실전투자

        params = {
            "FID_COND_MRKT_DIV_CODE": "J",  # 시장 분류 코드 (J: 주식)
            "FID_INPUT_ISCD": symbol_code,  # 종목 코드
            "FID_PERIOD_DIV_CODE": "D",  # 기간 분류 코드 (D: 일, W: 주, M: 월)
            "FID_ORG_ADJ_PRC": "0",  # 수정주가 여부 (0: 수정주가 반영, 1: 원주가)
        }

        try:
            # KIS API 호출
            res = ka._url_fetch(api_url, tr_id, "", params)

            if res.isOK():
                # output2에 일자별 데이터가 있음
                if hasattr(res.getBody(), "output2"):
                    df = pd.DataFrame(res.getBody().output2)
                    return df
                else:
                    print(f"  No data in response for {symbol_code}")
                    return pd.DataFrame()
            else:
                print(f"  API error for {symbol_code}: {res.getErrorMessage()}")
                return pd.DataFrame()

        except Exception as e:
            print(f"  Error fetching data for {symbol_code}: {e}")
            return pd.DataFrame()

    def _convert_kis_data_to_price_data(
        self, symbol_id: int, df: pd.DataFrame
    ) -> list[dict[str, Any]]:
        """
        Convert KIS API data to PriceData format.

        KIS API returns columns:
        - stck_bsop_date: 주식 영업 일자 (YYYYMMDD)
        - stck_oprc: 시가
        - stck_hgpr: 고가
        - stck_lwpr: 저가
        - stck_clpr: 종가 (현재가)
        - acml_vol: 누적 거래량
        - acml_tr_pbmn: 누적 거래 대금

        Args:
            symbol_id: Database symbol ID
            df: DataFrame from KIS API

        Returns:
            List of price data dictionaries
        """
        price_data_list = []

        for _, row in df.iterrows():
            try:
                # 날짜 파싱 (YYYYMMDD -> datetime)
                date_str = str(row.get("stck_bsop_date", ""))
                if not date_str or len(date_str) != 8:
                    continue

                timestamp = datetime.strptime(date_str, "%Y%m%d").replace(
                    tzinfo=timezone.utc
                )

                # 가격 데이터 추출 (문자열 -> Decimal)
                open_price = row.get("stck_oprc", "0")
                high_price = row.get("stck_hgpr", "0")
                low_price = row.get("stck_lwpr", "0")
                close_price = row.get("stck_clpr", "0")
                volume = row.get("acml_vol", "0")
                quote_volume = row.get("acml_tr_pbmn", "0")  # 거래대금 (KRW)

                # 빈 값 체크
                if not all([open_price, high_price, low_price, close_price]):
                    continue

                price_data = {
                    "symbol_id": symbol_id,
                    "timestamp": timestamp,
                    "open_price": Decimal(str(open_price)),
                    "high_price": Decimal(str(high_price)),
                    "low_price": Decimal(str(low_price)),
                    "close_price": Decimal(str(close_price)),
                    "volume": Decimal(str(volume)) if volume else Decimal("0"),
                    "quote_volume": (
                        Decimal(str(quote_volume)) if quote_volume else Decimal("0")
                    ),
                    "timeframe": "1d",  # 일봉 데이터
                }

                price_data_list.append(price_data)

            except (ValueError, KeyError) as e:
                print(f"  Error converting row: {e}")
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
                print(f"  Error saving price data for symbol_id {symbol_id}: {e}")
                skipped_count += 1
                continue

        # Commit all at once for better performance
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"  Error committing price data: {e}")
            return (0, len(price_data_list))

        return (created_count, skipped_count)

    def collect_symbol_price_data(
        self,
        symbol: Symbol,
        days_back: int = 1,
    ) -> tuple[int, int]:
        """
        Collect price data for a single symbol.

        Args:
            symbol: Symbol object from database
            days_back: Number of days to go back from today

        Returns:
            Tuple of (created_count, skipped_count)
        """
        # Calculate date range
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")

        print(
            f"Fetching daily data for {symbol.base_asset} ({symbol.symbol}, ID: {symbol.id})..."
        )

        # Fetch price data from KIS API
        df = self.fetch_daily_price(
            symbol_code=symbol.symbol, start_date=start_date, end_date=end_date
        )

        if df.empty:
            print(f"  No data fetched for {symbol.symbol}")
            return (0, 0)

        # Convert to price data format
        price_data_list = self._convert_kis_data_to_price_data(
            symbol_id=symbol.id, df=df
        )

        if not price_data_list:
            print(f"  No valid data for {symbol.symbol}")
            return (0, 0)

        # Save to database
        created, skipped = self.save_price_data(symbol.id, price_data_list)

        print(f"  {symbol.base_asset} ({symbol.symbol}): {created} created, {skipped} skipped")

        # Rate limiting: KIS API has rate limits (20 requests per second)
        import time

        time.sleep(0.05)  # 50ms delay between requests

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

        # Get stock symbols
        symbols = self._get_stock_symbols(market=market, limit=limit)

        market_str = market if market else "ALL"
        print(f"\nStarting price data collection for {len(symbols)} {market_str} symbols...")
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
        print(f"Collection completed!")
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
