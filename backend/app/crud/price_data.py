from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.models.price_data import PriceData, PriceDataCreate, PriceDataUpdate


def create_price_data(
    *, session: Session, price_data_create: PriceDataCreate
) -> PriceData:
    """
    가격 데이터 생성
    """
    db_obj = PriceData.model_validate(price_data_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def bulk_create_price_data(
    *, session: Session, price_data_list: list[PriceDataCreate]
) -> list[PriceData]:
    """
    가격 데이터 대량 생성 (배치 삽입)
    """
    db_objs = [PriceData.model_validate(item) for item in price_data_list]
    session.add_all(db_objs)
    session.commit()
    for obj in db_objs:
        session.refresh(obj)
    return db_objs


def get_price_data(*, session: Session, price_data_id: int) -> PriceData | None:
    """
    ID로 가격 데이터 조회
    """
    statement = select(PriceData).where(PriceData.id == price_data_id)
    return session.exec(statement).first()


def get_price_data_by_symbol(
    *,
    session: Session,
    symbol_id: int,
    timeframe: str,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    skip: int = 0,
    limit: int = 1000,
) -> list[PriceData]:
    """
    특정 종목의 가격 데이터 조회 (시간 범위 필터 가능)

    Args:
        session: 데이터베이스 세션
        symbol_id: 종목 ID
        timeframe: 시간 프레임 ('1d', '1h' 등)
        start_time: 시작 시간 (포함)
        end_time: 종료 시간 (포함)
        skip: 페이지네이션 offset
        limit: 페이지네이션 limit (최대 1000)
    """
    statement = select(PriceData).where(
        PriceData.symbol_id == symbol_id, PriceData.timeframe == timeframe
    )

    if start_time:
        statement = statement.where(PriceData.timestamp >= start_time)
    if end_time:
        statement = statement.where(PriceData.timestamp <= end_time)

    # 시간 역순 정렬 (최신 데이터 먼저)
    statement = statement.order_by(PriceData.timestamp.desc()).offset(skip).limit(limit)

    return list(session.exec(statement).all())


def get_latest_price_data(
    *, session: Session, symbol_id: int, timeframe: str
) -> PriceData | None:
    """
    특정 종목의 가장 최신 가격 데이터 조회
    """
    statement = (
        select(PriceData)
        .where(PriceData.symbol_id == symbol_id, PriceData.timeframe == timeframe)
        .order_by(PriceData.timestamp.desc())
        .limit(1)
    )
    return session.exec(statement).first()


def get_price_data_by_timestamp(
    *,
    session: Session,
    symbol_id: int,
    timestamp: datetime,
    timeframe: str,
) -> PriceData | None:
    """
    특정 종목의 특정 시각 가격 데이터 조회
    """
    statement = select(PriceData).where(
        PriceData.symbol_id == symbol_id,
        PriceData.timestamp == timestamp,
        PriceData.timeframe == timeframe,
    )
    return session.exec(statement).first()


def update_price_data(
    *, session: Session, db_price_data: PriceData, price_data_in: PriceDataUpdate
) -> Any:
    """
    가격 데이터 업데이트 (일반적으로 가격 데이터는 수정하지 않지만 필요시 사용)
    """
    price_data_dict = price_data_in.model_dump(exclude_unset=True)
    db_price_data.sqlmodel_update(price_data_dict)
    session.add(db_price_data)
    session.commit()
    session.refresh(db_price_data)
    return db_price_data


def delete_price_data(*, session: Session, price_data_id: int) -> bool:
    """
    가격 데이터 삭제
    """
    price_data = get_price_data(session=session, price_data_id=price_data_id)
    if price_data:
        session.delete(price_data)
        session.commit()
        return True
    return False


def delete_price_data_by_symbol(
    *, session: Session, symbol_id: int, timeframe: str | None = None
) -> int:
    """
    특정 종목의 가격 데이터 삭제 (timeframe 지정 가능)

    Returns:
        삭제된 레코드 수
    """
    statement = select(PriceData).where(PriceData.symbol_id == symbol_id)
    if timeframe:
        statement = statement.where(PriceData.timeframe == timeframe)

    price_data_list = session.exec(statement).all()
    count = len(price_data_list)

    for price_data in price_data_list:
        session.delete(price_data)

    session.commit()
    return count
