"""
Trading Strategies Model

매매 전략 및 전략-종목 매핑 관리
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, JSON, UniqueConstraint
from sqlmodel import Column, Field, SQLModel


class TradingStrategyBase(SQLModel):
    name: str = Field(max_length=200, nullable=False)
    strategy_type: str = Field(
        max_length=50, nullable=False
    )  # 'GRID', 'REBALANCING', 'DCA' 등
    description: str | None = Field(default=None)
    config: dict = Field(
        default_factory=dict, sa_column=Column(JSON, nullable=False)
    )  # 전략별 설정 데이터 (JSONB)
    is_active: bool = Field(default=False)


class TradingStrategyCreate(TradingStrategyBase):
    pass


class TradingStrategyUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=200)
    strategy_type: str | None = Field(default=None, max_length=50)
    description: str | None = None
    config: dict | None = None
    is_active: bool | None = None


class TradingStrategy(TradingStrategyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # 외래 키: users 테이블 참조 (CASCADE 삭제)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )


class TradingStrategyPublic(TradingStrategyBase):
    id: int
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TradingStrategiesPublic(SQLModel):
    data: list[TradingStrategyPublic]
    count: int


# Strategy Symbols (전략-종목 매핑)
class StrategySymbolBase(SQLModel):
    strategy_id: int = Field(foreign_key="tradingstrategy.id", nullable=False)
    symbol_id: int = Field(foreign_key="symbol.id", nullable=False)
    allocation_ratio: Decimal = Field(
        default=Decimal("0.0"), max_digits=5, decimal_places=4
    )  # 비중 (0.0 ~ 1.0)
    is_active: bool = Field(default=True)


class StrategySymbolCreate(StrategySymbolBase):
    pass


class StrategySymbolUpdate(SQLModel):
    strategy_id: int | None = None
    symbol_id: int | None = None
    allocation_ratio: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=4
    )
    is_active: bool | None = None


class StrategySymbol(StrategySymbolBase, table=True):
    __table_args__ = (
        UniqueConstraint("strategy_id", "symbol_id", name="uq_strategy_symbol"),
    )

    id: int | None = Field(default=None, primary_key=True)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )


class StrategySymbolPublic(StrategySymbolBase):
    id: int
    created_at: datetime


class StrategySymbolsPublic(SQLModel):
    data: list[StrategySymbolPublic]
    count: int
