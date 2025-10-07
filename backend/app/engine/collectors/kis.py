"""
KIS (Korea Investment & Securities) Collector

Collects Korean stock symbol data from KRX master files.
Uses the open-trading-api submodule's stock info code.
"""

import os
import ssl
import urllib.request
import zipfile
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models.exchanges import Exchange
from app.models.symbols import Symbol

from .base import BaseCollector


class KISCollector(BaseCollector):
    """Collector for KIS (Korea Investment & Securities) stock data."""

    def __init__(self, session: Session):
        """
        Initialize KIS collector.

        Args:
            session: Database session for data persistence
        """
        super().__init__(session)
        self.exchange_code = "kis"
        self.exchange_id: int | None = None

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

    def _download_master_file(
        self, market: str, base_dir: str, verbose: bool = False
    ) -> None:
        """
        Download master file for specified market.

        Args:
            market: Market type ("kospi" or "kosdaq")
            base_dir: Base directory to save files
            verbose: Print verbose output
        """
        if verbose:
            print(f"Downloading {market.upper()} master file...")

        ssl._create_default_https_context = ssl._create_unverified_context

        url = f"https://new.real.download.dws.co.kr/common/master/{market}_code.mst.zip"
        zip_path = os.path.join(base_dir, f"{market}_code.zip")

        urllib.request.urlretrieve(url, zip_path)

        with zipfile.ZipFile(zip_path) as zip_file:
            zip_file.extractall(base_dir)

        if os.path.exists(zip_path):
            os.remove(zip_path)

    def _parse_kospi_master(self, base_dir: str) -> pd.DataFrame:
        """
        Parse KOSPI master file.

        Args:
            base_dir: Base directory containing master files

        Returns:
            DataFrame with KOSPI stock data
        """
        file_name = os.path.join(base_dir, "kospi_code.mst")
        tmp_fil1 = os.path.join(base_dir, "kospi_code_part1.tmp")
        tmp_fil2 = os.path.join(base_dir, "kospi_code_part2.tmp")

        with open(tmp_fil1, mode="w", encoding="utf-8") as wf1, open(
            tmp_fil2, mode="w", encoding="utf-8"
        ) as wf2:
            with open(file_name, mode="r", encoding="cp949", errors="ignore") as f:
                for row in f:
                    rf1 = row[0 : len(row) - 228]
                    rf1_1 = rf1[0:9].rstrip()
                    rf1_2 = rf1[9:21].rstrip()
                    rf1_3 = rf1[21:].strip()
                    wf1.write(rf1_1 + "," + rf1_2 + "," + rf1_3 + "\n")
                    rf2 = row[-228:]
                    wf2.write(rf2)

        part1_columns = ["단축코드", "표준코드", "한글명"]
        df1 = pd.read_csv(tmp_fil1, header=None, names=part1_columns, encoding="utf-8")

        field_specs = [
            2,
            1,
            4,
            4,
            4,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            9,
            5,
            5,
            1,
            1,
            1,
            2,
            1,
            1,
            1,
            2,
            2,
            2,
            3,
            1,
            3,
            12,
            12,
            8,
            15,
            21,
            2,
            7,
            1,
            1,
            1,
            1,
            1,
            9,
            9,
            9,
            5,
            9,
            8,
            9,
            3,
            1,
            1,
            1,
        ]

        part2_columns = [
            "그룹코드",
            "시가총액규모",
            "지수업종대분류",
            "지수업종중분류",
            "지수업종소분류",
            "제조업",
            "저유동성",
            "지배구조지수종목",
            "KOSPI200섹터업종",
            "KOSPI100",
            "KOSPI50",
            "KRX",
            "ETP",
            "ELW발행",
            "KRX100",
            "KRX자동차",
            "KRX반도체",
            "KRX바이오",
            "KRX은행",
            "SPAC",
            "KRX에너지화학",
            "KRX철강",
            "단기과열",
            "KRX미디어통신",
            "KRX건설",
            "Non1",
            "KRX증권",
            "KRX선박",
            "KRX섹터_보험",
            "KRX섹터_운송",
            "SRI",
            "기준가",
            "매매수량단위",
            "시간외수량단위",
            "거래정지",
            "정리매매",
            "관리종목",
            "시장경고",
            "경고예고",
            "불성실공시",
            "우회상장",
            "락구분",
            "액면변경",
            "증자구분",
            "증거금비율",
            "신용가능",
            "신용기간",
            "전일거래량",
            "액면가",
            "상장일자",
            "상장주수",
            "자본금",
            "결산월",
            "공모가",
            "우선주",
            "공매도과열",
            "이상급등",
            "KRX300",
            "KOSPI",
            "매출액",
            "영업이익",
            "경상이익",
            "당기순이익",
            "ROE",
            "기준년월",
            "시가총액",
            "그룹사코드",
            "회사신용한도초과",
            "담보대출가능",
            "대주가능",
        ]

        df2 = pd.read_fwf(tmp_fil2, widths=field_specs, names=part2_columns)

        df = pd.merge(df1, df2, how="outer", left_index=True, right_index=True)

        # Clean up temporary files
        os.remove(tmp_fil1)
        os.remove(tmp_fil2)

        return df

    def _parse_kosdaq_master(self, base_dir: str) -> pd.DataFrame:
        """
        Parse KOSDAQ master file.

        Args:
            base_dir: Base directory containing master files

        Returns:
            DataFrame with KOSDAQ stock data
        """
        file_name = os.path.join(base_dir, "kosdaq_code.mst")
        tmp_fil1 = os.path.join(base_dir, "kosdaq_code_part1.tmp")
        tmp_fil2 = os.path.join(base_dir, "kosdaq_code_part2.tmp")

        with open(tmp_fil1, mode="w", encoding="utf-8") as wf1, open(
            tmp_fil2, mode="w", encoding="utf-8"
        ) as wf2:
            with open(file_name, mode="r", encoding="cp949", errors="ignore") as f:
                for row in f:
                    rf1 = row[0 : len(row) - 222]
                    rf1_1 = rf1[0:9].rstrip()
                    rf1_2 = rf1[9:21].rstrip()
                    rf1_3 = rf1[21:].strip()
                    wf1.write(rf1_1 + "," + rf1_2 + "," + rf1_3 + "\n")
                    rf2 = row[-222:]
                    wf2.write(rf2)

        part1_columns = ["단축코드", "표준코드", "한글종목명"]
        df1 = pd.read_csv(tmp_fil1, header=None, names=part1_columns, encoding="utf-8")

        field_specs = [
            2,
            1,
            4,
            4,
            4,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            9,
            5,
            5,
            1,
            1,
            1,
            2,
            1,
            1,
            1,
            2,
            2,
            2,
            3,
            1,
            3,
            12,
            12,
            8,
            15,
            21,
            2,
            7,
            1,
            1,
            1,
            1,
            9,
            9,
            9,
            5,
            9,
            8,
            9,
            3,
            1,
            1,
            1,
        ]

        part2_columns = [
            "증권그룹구분코드",
            "시가총액 규모 구분 코드 유가",
            "지수업종 대분류 코드",
            "지수 업종 중분류 코드",
            "지수업종 소분류 코드",
            "벤처기업 여부 (Y/N)",
            "저유동성종목 여부",
            "KRX 종목 여부",
            "ETP 상품구분코드",
            "KRX100 종목 여부 (Y/N)",
            "KRX 자동차 여부",
            "KRX 반도체 여부",
            "KRX 바이오 여부",
            "KRX 은행 여부",
            "기업인수목적회사여부",
            "KRX 에너지 화학 여부",
            "KRX 철강 여부",
            "단기과열종목구분코드",
            "KRX 미디어 통신 여부",
            "KRX 건설 여부",
            "(코스닥)투자주의환기종목여부",
            "KRX 증권 구분",
            "KRX 선박 구분",
            "KRX섹터지수 보험여부",
            "KRX섹터지수 운송여부",
            "KOSDAQ150지수여부 (Y,N)",
            "주식 기준가",
            "정규 시장 매매 수량 단위",
            "시간외 시장 매매 수량 단위",
            "거래정지 여부",
            "정리매매 여부",
            "관리 종목 여부",
            "시장 경고 구분 코드",
            "시장 경고위험 예고 여부",
            "불성실 공시 여부",
            "우회 상장 여부",
            "락구분 코드",
            "액면가 변경 구분 코드",
            "증자 구분 코드",
            "증거금 비율",
            "신용주문 가능 여부",
            "신용기간",
            "전일 거래량",
            "주식 액면가",
            "주식 상장 일자",
            "상장 주수(천)",
            "자본금",
            "결산 월",
            "공모 가격",
            "우선주 구분 코드",
            "공매도과열종목여부",
            "이상급등종목여부",
            "KRX300 종목 여부 (Y/N)",
            "매출액",
            "영업이익",
            "경상이익",
            "단기순이익",
            "ROE(자기자본이익률)",
            "기준년월",
            "전일기준 시가총액 (억)",
            "그룹사 코드",
            "회사신용한도초과여부",
            "담보대출가능여부",
            "대주가능여부",
        ]

        df2 = pd.read_fwf(tmp_fil2, widths=field_specs, names=part2_columns)

        df = pd.merge(df1, df2, how="outer", left_index=True, right_index=True)

        # Clean up temporary files
        os.remove(tmp_fil1)
        os.remove(tmp_fil2)

        return df

    async def fetch_symbols(self) -> list[dict[str, Any]]:
        """
        Fetch stock symbols from KRX master files.

        Returns:
            List of symbol data dictionaries
        """
        self._init_exchange()

        symbols_data = []

        # Create temporary directory for master files
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            # Fetch KOSPI and KOSDAQ symbols
            for market in ["kospi", "kosdaq"]:
                try:
                    # Download master file
                    self._download_master_file(market, temp_dir)

                    # Parse master file
                    if market == "kospi":
                        df = self._parse_kospi_master(temp_dir)
                        market_name = "KOSPI"
                    else:
                        df = self._parse_kosdaq_master(temp_dir)
                        market_name = "KOSDAQ"

                    # Convert DataFrame to symbol data
                    for _, row in df.iterrows():
                        ticker = row["단축코드"]
                        stock_name = (
                            row["한글명"] if market == "kospi" else row["한글종목명"]
                        )

                        # Skip if ticker or stock name is invalid
                        if pd.isna(ticker) or pd.isna(stock_name):
                            continue

                        # Korean stock market specifications:
                        # - Price precision: 0 (integer prices in KRW)
                        # - Quantity precision: 0 (whole numbers)
                        # - Minimum order: 1 share
                        # - Maximum order: no strict limit (using large default)

                        symbol_data = {
                            "exchange_id": self.exchange_id,
                            "symbol": str(
                                ticker
                            ).strip(),  # e.g., "005930" for Samsung Electronics
                            "base_asset": str(stock_name).strip(),  # e.g., "삼성전자"
                            "quote_asset": "KRW",
                            "symbol_type": "STOCK",
                            "market": market_name,  # "KOSPI" or "KOSDAQ"
                            "is_active": True,
                            "min_order_size": Decimal("1"),  # Minimum 1 share
                            "max_order_size": Decimal(
                                "1000000000"
                            ),  # 1 billion shares (default)
                            "price_precision": 0,  # KRW markets use integer prices
                            "quantity_precision": 0,  # Stocks are traded in whole numbers
                        }

                        symbols_data.append(symbol_data)

                except Exception as e:
                    print(f"Error fetching {market.upper()} symbols: {e}")
                    continue

        return symbols_data

    async def save_symbols(self, symbols_data: list[dict[str, Any]]) -> int:
        """
        Save symbols to the database.

        Args:
            symbols_data: List of symbol data dictionaries

        Returns:
            Number of symbols saved (created or updated)
        """
        saved_count = 0
        updated_count = 0

        for symbol_data in symbols_data:
            try:
                # Check if symbol already exists
                statement = select(Symbol).where(
                    Symbol.exchange_id == symbol_data["exchange_id"],
                    Symbol.symbol == symbol_data["symbol"],
                )
                existing_symbol = self.session.exec(statement).first()

                if existing_symbol:
                    # Update existing symbol
                    for key, value in symbol_data.items():
                        setattr(existing_symbol, key, value)
                    existing_symbol.updated_at = datetime.now(timezone.utc)
                    updated_count += 1
                else:
                    # Create new symbol
                    symbol = Symbol(**symbol_data)
                    self.session.add(symbol)
                    saved_count += 1

                self.session.commit()

            except IntegrityError as e:
                self.session.rollback()
                print(f"Error saving symbol {symbol_data.get('symbol')}: {e}")
                continue

        total_count = saved_count + updated_count
        print(
            f"KIS: {saved_count} symbols created, {updated_count} symbols updated. "
            f"Total: {total_count}"
        )

        return total_count
