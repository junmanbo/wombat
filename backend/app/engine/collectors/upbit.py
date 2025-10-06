"""
Upbit Collector

Collects cryptocurrency symbol data from Upbit exchange using ccxt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import ccxt.async_support as ccxt
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models.exchanges import Exchange
from app.models.symbols import Symbol

from .base import BaseCollector


class UpbitCollector(BaseCollector):
    """Collector for Upbit exchange cryptocurrency data."""

    def __init__(self, session: Session):
        """
        Initialize Upbit collector.

        Args:
            session: Database session for data persistence
        """
        super().__init__(session)
        self.exchange_code = "upbit"
        self.exchange_id: int | None = None
        self.ccxt_exchange: ccxt.upbit | None = None

    def _precision_from_step_size(self, step_size: float) -> int:
        """
        Convert step size to decimal places.

        Args:
            step_size: Minimum step size (e.g., 0.00000001 or 1e-08)

        Returns:
            Number of decimal places (e.g., 8)
        """
        if step_size >= 1:
            return 0

        # Convert to string and count decimal places
        step_str = f"{step_size:.10f}".rstrip("0")
        if "." in step_str:
            return len(step_str.split(".")[1])
        return 0

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

    async def fetch_symbols(self) -> list[dict[str, Any]]:
        """
        Fetch cryptocurrency symbols from Upbit.

        Returns:
            List of symbol data dictionaries
        """
        await self._init_exchange()

        if not self.ccxt_exchange:
            raise RuntimeError("Exchange not initialized")

        try:
            # Load markets from Upbit
            markets = await self.ccxt_exchange.load_markets()

            symbols_data = []

            for symbol, market in markets.items():
                # Upbit uses KRW as the main quote currency
                if not market.get("quote") == "KRW":
                    continue

                # Extract market information
                base = market.get("base", "")
                quote = market.get("quote", "")
                symbol_str = market.get("symbol", "")  # e.g., "BTC/KRW"

                # Get precision and limits from ccxt
                precision = market.get("precision", {})
                limits = market.get("limits", {})

                # Upbit KRW market has fixed order amount limits
                # Source: https://support.upbit.com/hc/ko/articles/900005982246
                # Minimum order amount: 5,000 KRW
                # Maximum order amount: 1,000,000,000 KRW (1 billion)
                cost_limits = limits.get("cost", {})
                min_cost = cost_limits.get("min") if cost_limits else None
                max_cost = cost_limits.get("max") if cost_limits else None

                # Use default values if not provided
                if min_cost is None:
                    min_cost = 5000
                if max_cost is None:
                    max_cost = 1000000000

                # Convert precision from minimum step size to decimal places
                # e.g., 1e-08 (0.00000001) -> 8 decimal places
                amount_prec = precision.get("amount")
                if amount_prec is not None and amount_prec > 0:
                    # Calculate decimal places from step size
                    amount_precision = self._precision_from_step_size(amount_prec)
                else:
                    amount_precision = 8  # Default for crypto

                price_prec = precision.get("price")
                if price_prec is not None and price_prec > 0:
                    # Calculate decimal places from step size
                    price_precision = self._precision_from_step_size(price_prec)
                else:
                    price_precision = 0  # KRW markets typically use integer prices

                symbol_data = {
                    "exchange_id": self.exchange_id,
                    "symbol": symbol_str,
                    "base_asset": base,
                    "quote_asset": quote,
                    "symbol_type": "CRYPTO",
                    "market": "KRW",
                    "is_active": market.get("active", True),
                    "min_order_size": Decimal(str(min_cost)),
                    "max_order_size": Decimal(str(max_cost)),
                    "price_precision": int(price_precision),
                    "quantity_precision": int(amount_precision),
                }

                symbols_data.append(symbol_data)

            return symbols_data

        finally:
            # Clean up
            if self.ccxt_exchange:
                await self.ccxt_exchange.close()
                self.ccxt_exchange = None

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
            f"Upbit: {saved_count} symbols created, {updated_count} symbols updated. "
            f"Total: {total_count}"
        )

        return total_count
