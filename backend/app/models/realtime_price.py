from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, UniqueConstraint
from sqlmodel import Field, SQLModel


class RealtimePriceBase(SQLModel):
    # 외래 키: symbols 테이블 참조 (종목 ID)
    symbol_id: int = Field(foreign_key="symbol.id", nullable=False)

    # 현재가: 최근 체결된 거래 가격
    current_price: Decimal = Field(max_digits=20, decimal_places=8, nullable=False)

    # 매수 호가: 가장 높은 매수 주문 가격
    bid_price: Decimal | None = Field(default=None, max_digits=20, decimal_places=8)

    # 매도 호가: 가장 낮은 매도 주문 가격
    ask_price: Decimal | None = Field(default=None, max_digits=20, decimal_places=8)

    # 24시간 거래량
    volume_24h: Decimal | None = Field(default=None, max_digits=20, decimal_places=8)

    # 변동률: 전일 대비 가격 변동 비율 (%)
    change_rate: Decimal | None = Field(default=None, max_digits=8, decimal_places=4)


class RealtimePriceCreate(RealtimePriceBase):
    pass


class RealtimePriceUpdate(SQLModel):
    symbol_id: int | None = None
    current_price: Decimal | None = Field(default=None, max_digits=20, decimal_places=8)
    bid_price: Decimal | None = Field(default=None, max_digits=20, decimal_places=8)
    ask_price: Decimal | None = Field(default=None, max_digits=20, decimal_places=8)
    volume_24h: Decimal | None = Field(default=None, max_digits=20, decimal_places=8)
    change_rate: Decimal | None = Field(default=None, max_digits=8, decimal_places=4)


class RealtimePrice(RealtimePriceBase, table=True):
    # 테이블 이름 명시
    __tablename__ = "realtime_prices"

    # 유니크 제약: 동일 종목은 하나의 실시간 가격 데이터만 존재
    __table_args__ = (
        UniqueConstraint("symbol_id", name="uq_realtime_price_symbol"),
    )

    # 프라이머리 키: 자동 증가 정수
    id: int | None = Field(default=None, primary_key=True)

    # 데이터 갱신 시각: 실시간 가격이 마지막으로 업데이트된 시간
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )


class RealtimePricePublic(RealtimePriceBase):
    id: int
    updated_at: datetime


class RealtimePriceListPublic(SQLModel):
    data: list[RealtimePricePublic]
    count: int
