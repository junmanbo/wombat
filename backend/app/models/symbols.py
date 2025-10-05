from datetime import datetime, timezone
from decimal import Decimal

from sqlmodel import Field, SQLModel


class SymbolBase(SQLModel):
    exchange_id: int = Field(foreign_key="exchange.id")
    symbol: str = Field(max_length=50)  # 'KRW-BTC', '005930' 등
    base_asset: str | None = Field(default=None, max_length=20)  # 'BTC', '삼성전자' 등
    quote_asset: str | None = Field(default=None, max_length=20)  # 'KRW', 'USDT' 등
    symbol_type: str = Field(max_length=20)  # 'STOCK', 'CRYPTO'
    market: str | None = Field(
        default=None, max_length=20
    )  # 'KOSPI', 'KOSDAQ', 'KRW' 등
    is_active: bool = True
    min_order_size: Decimal | None = Field(
        default=None, max_digits=20, decimal_places=8
    )
    max_order_size: Decimal | None = Field(
        default=None, max_digits=20, decimal_places=8
    )
    price_precision: int = 0
    quantity_precision: int = 0


class SymbolCreate(SymbolBase):
    pass


class SymbolUpdate(SQLModel):
    exchange_id: int | None = None
    symbol: str | None = Field(default=None, max_length=50)
    base_asset: str | None = Field(default=None, max_length=20)
    quote_asset: str | None = Field(default=None, max_length=20)
    symbol_type: str | None = Field(default=None, max_length=20)
    market: str | None = Field(default=None, max_length=20)
    is_active: bool | None = None
    min_order_size: Decimal | None = Field(
        default=None, max_digits=20, decimal_places=8
    )
    max_order_size: Decimal | None = Field(
        default=None, max_digits=20, decimal_places=8
    )
    price_precision: int | None = None
    quantity_precision: int | None = None


class Symbol(SymbolBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        # UNIQUE(exchange_id, symbol) 제약조건은 Alembic migration에서 추가 필요
        pass


class SymbolPublic(SymbolBase):
    id: int
    created_at: datetime
    updated_at: datetime


class SymbolsPublic(SQLModel):
    data: list[SymbolPublic]
    count: int
