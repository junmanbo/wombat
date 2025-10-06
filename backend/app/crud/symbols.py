from typing import Any

from sqlmodel import Session, select

from app.models.symbols import Symbol, SymbolCreate, SymbolUpdate


def create_symbol(*, session: Session, symbol_create: SymbolCreate) -> Symbol:
    db_obj = Symbol.model_validate(symbol_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_symbol(*, session: Session, symbol_id: int) -> Symbol | None:
    statement = select(Symbol).where(Symbol.id == symbol_id)
    return session.exec(statement).first()


def get_symbol_by_exchange_and_code(
    *, session: Session, exchange_id: int, symbol: str
) -> Symbol | None:
    statement = select(Symbol).where(
        Symbol.exchange_id == exchange_id, Symbol.symbol == symbol
    )
    return session.exec(statement).first()


def get_symbols(*, session: Session, skip: int = 0, limit: int = 100) -> list[Symbol]:
    statement = select(Symbol).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_symbols_by_exchange(
    *, session: Session, exchange_id: int, skip: int = 0, limit: int = 100
) -> list[Symbol]:
    statement = (
        select(Symbol)
        .where(Symbol.exchange_id == exchange_id)
        .offset(skip)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def update_symbol(
    *, session: Session, db_symbol: Symbol, symbol_in: SymbolUpdate
) -> Any:
    symbol_data = symbol_in.model_dump(exclude_unset=True)
    db_symbol.sqlmodel_update(symbol_data)
    session.add(db_symbol)
    session.commit()
    session.refresh(db_symbol)
    return db_symbol


def delete_symbol(*, session: Session, symbol_id: int) -> bool:
    symbol = get_symbol(session=session, symbol_id=symbol_id)
    if symbol:
        session.delete(symbol)
        session.commit()
        return True
    return False
