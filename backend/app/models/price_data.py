from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, Index, UniqueConstraint
from sqlmodel import Field, SQLModel


class PriceDataBase(SQLModel):
    # 외래 키: symbols 테이블 참조 (종목 ID)
    symbol_id: int = Field(foreign_key="symbol.id", nullable=False)

    # 가격 데이터 타임스탬프 (해당 봉의 시작 시간)
    timestamp: datetime = Field(nullable=False, sa_type=DateTime(timezone=True))

    # 시가: 해당 기간의 첫 거래 가격
    open_price: Decimal = Field(max_digits=20, decimal_places=8, nullable=False)

    # 고가: 해당 기간의 최고 거래 가격
    high_price: Decimal = Field(max_digits=20, decimal_places=8, nullable=False)

    # 저가: 해당 기간의 최저 거래 가격
    low_price: Decimal = Field(max_digits=20, decimal_places=8, nullable=False)

    # 종가: 해당 기간의 마지막 거래 가격
    close_price: Decimal = Field(max_digits=20, decimal_places=8, nullable=False)

    # 거래량: 해당 기간의 총 거래량 (주식: 주, 암호화폐: 코인 수량)
    volume: Decimal = Field(max_digits=30, decimal_places=8, nullable=False)

    # 거래대금: 해당 기간의 총 거래금액 (quote currency 기준)
    quote_volume: Decimal | None = Field(default=None, max_digits=30, decimal_places=8)

    # 시간 프레임: 봉의 주기 ('1m', '5m', '15m', '1h', '4h', '1d' 등)
    timeframe: str = Field(max_length=10, nullable=False)


class PriceDataCreate(PriceDataBase):
    pass


class PriceDataUpdate(SQLModel):
    symbol_id: int | None = None
    timestamp: datetime | None = None
    open_price: Decimal | None = Field(default=None, max_digits=20, decimal_places=8)
    high_price: Decimal | None = Field(default=None, max_digits=20, decimal_places=8)
    low_price: Decimal | None = Field(default=None, max_digits=20, decimal_places=8)
    close_price: Decimal | None = Field(default=None, max_digits=20, decimal_places=8)
    volume: Decimal | None = Field(default=None, max_digits=30, decimal_places=8)
    quote_volume: Decimal | None = Field(default=None, max_digits=30, decimal_places=8)
    timeframe: str | None = Field(default=None, max_length=10)


class PriceData(PriceDataBase, table=True):
    # 복합 유니크 제약: 동일 종목, 타임스탬프, 시간프레임 조합은 유일해야 함
    # 예: 삼성전자(symbol_id=1)의 2024-01-01 09:00:00 1일봉 데이터는 단 하나만 존재
    __table_args__ = (
        UniqueConstraint(
            "symbol_id", "timestamp", "timeframe", name="uq_symbol_time_frame"
        ),
        # 시계열 조회 최적화: 종목별 최신 데이터 조회용 인덱스 (내림차순)
        Index(
            "idx_price_data_symbol_time",
            "symbol_id",
            "timestamp",
            postgresql_ops={"timestamp": "DESC"},
        ),
        # 시간프레임별 조회 최적화: 특정 봉 주기의 최신 데이터 조회용 인덱스
        Index(
            "idx_price_data_timeframe",
            "timeframe",
            "timestamp",
            postgresql_ops={"timestamp": "DESC"},
        ),
    )

    # 프라이머리 키: 자동 증가 정수 (BIGSERIAL)
    id: int | None = Field(default=None, primary_key=True)

    # 데이터 생성 시각: 레코드가 데이터베이스에 삽입된 시간
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )


class PriceDataPublic(PriceDataBase):
    id: int
    created_at: datetime


class PriceDataListPublic(SQLModel):
    data: list[PriceDataPublic]
    count: int
