from typing import Any

from sqlmodel import Session, select

from app.models.realtime_price import (
    RealtimePrice,
    RealtimePriceCreate,
    RealtimePriceUpdate,
)


def create_realtime_price(
    *, session: Session, realtime_price_create: RealtimePriceCreate
) -> RealtimePrice:
    """
    실시간 가격 데이터 생성
    """
    db_obj = RealtimePrice.model_validate(realtime_price_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def upsert_realtime_price(
    *, session: Session, realtime_price_create: RealtimePriceCreate
) -> RealtimePrice:
    """
    실시간 가격 데이터 생성 또는 업데이트 (UPSERT)
    동일한 symbol_id가 존재하면 업데이트, 없으면 생성
    """
    existing = get_realtime_price_by_symbol(
        session=session, symbol_id=realtime_price_create.symbol_id
    )

    if existing:
        # 기존 데이터 업데이트
        update_data = RealtimePriceUpdate.model_validate(realtime_price_create)
        return update_realtime_price(
            session=session, db_realtime_price=existing, realtime_price_in=update_data
        )
    else:
        # 새로운 데이터 생성
        return create_realtime_price(
            session=session, realtime_price_create=realtime_price_create
        )


def bulk_upsert_realtime_prices(
    *, session: Session, realtime_price_list: list[RealtimePriceCreate]
) -> list[RealtimePrice]:
    """
    실시간 가격 데이터 대량 생성/업데이트
    """
    result = []
    for item in realtime_price_list:
        upserted = upsert_realtime_price(session=session, realtime_price_create=item)
        result.append(upserted)
    return result


def get_realtime_price(
    *, session: Session, realtime_price_id: int
) -> RealtimePrice | None:
    """
    ID로 실시간 가격 데이터 조회
    """
    statement = select(RealtimePrice).where(RealtimePrice.id == realtime_price_id)
    return session.exec(statement).first()


def get_realtime_price_by_symbol(
    *, session: Session, symbol_id: int
) -> RealtimePrice | None:
    """
    특정 종목의 실시간 가격 데이터 조회
    """
    statement = select(RealtimePrice).where(RealtimePrice.symbol_id == symbol_id)
    return session.exec(statement).first()


def get_realtime_prices(
    *, session: Session, skip: int = 0, limit: int = 100
) -> list[RealtimePrice]:
    """
    모든 실시간 가격 데이터 조회 (페이지네이션)
    """
    statement = (
        select(RealtimePrice)
        .order_by(RealtimePrice.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def get_realtime_prices_by_symbols(
    *, session: Session, symbol_ids: list[int]
) -> list[RealtimePrice]:
    """
    여러 종목의 실시간 가격 데이터 조회
    """
    statement = select(RealtimePrice).where(RealtimePrice.symbol_id.in_(symbol_ids))
    return list(session.exec(statement).all())


def update_realtime_price(
    *,
    session: Session,
    db_realtime_price: RealtimePrice,
    realtime_price_in: RealtimePriceUpdate,
) -> Any:
    """
    실시간 가격 데이터 업데이트
    """
    realtime_price_dict = realtime_price_in.model_dump(exclude_unset=True)
    db_realtime_price.sqlmodel_update(realtime_price_dict)
    session.add(db_realtime_price)
    session.commit()
    session.refresh(db_realtime_price)
    return db_realtime_price


def delete_realtime_price(*, session: Session, realtime_price_id: int) -> bool:
    """
    실시간 가격 데이터 삭제
    """
    realtime_price = get_realtime_price(
        session=session, realtime_price_id=realtime_price_id
    )
    if realtime_price:
        session.delete(realtime_price)
        session.commit()
        return True
    return False


def delete_realtime_price_by_symbol(*, session: Session, symbol_id: int) -> bool:
    """
    특정 종목의 실시간 가격 데이터 삭제
    """
    realtime_price = get_realtime_price_by_symbol(session=session, symbol_id=symbol_id)
    if realtime_price:
        session.delete(realtime_price)
        session.commit()
        return True
    return False
