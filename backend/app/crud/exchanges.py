from typing import Any

from sqlmodel import Session, select

from app.models.exchanges import Exchange, ExchangeCreate, ExchangeUpdate


def create_exchange(*, session: Session, exchange_create: ExchangeCreate) -> Exchange:
    db_obj = Exchange.model_validate(exchange_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_exchange(*, session: Session, exchange_id: int) -> Exchange | None:
    statement = select(Exchange).where(Exchange.id == exchange_id)
    return session.exec(statement).first()


def get_exchange_by_code(*, session: Session, code: str) -> Exchange | None:
    statement = select(Exchange).where(Exchange.code == code)
    return session.exec(statement).first()


def get_exchanges(
    *, session: Session, skip: int = 0, limit: int = 100
) -> list[Exchange]:
    statement = select(Exchange).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_exchange(
    *, session: Session, db_exchange: Exchange, exchange_in: ExchangeUpdate
) -> Any:
    exchange_data = exchange_in.model_dump(exclude_unset=True)
    db_exchange.sqlmodel_update(exchange_data)
    session.add(db_exchange)
    session.commit()
    session.refresh(db_exchange)
    return db_exchange


def delete_exchange(*, session: Session, exchange_id: int) -> bool:
    exchange = get_exchange(session=session, exchange_id=exchange_id)
    if exchange:
        session.delete(exchange)
        session.commit()
        return True
    return False

