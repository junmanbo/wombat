from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.crud import symbols as crud_symbol
from app.models.symbols import (
    Symbol,
    SymbolCreate,
    SymbolPublic,
    SymbolsPublic,
    SymbolUpdate,
)
from app.models.users import Message

router = APIRouter(prefix="/symbols", tags=["symbols"])


@router.get("/", response_model=SymbolsPublic)
def read_symbols(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve symbols.
    """
    count_statement = select(func.count()).select_from(Symbol)
    count = session.exec(count_statement).one()

    statement = select(Symbol).offset(skip).limit(limit)
    symbols = session.exec(statement).all()

    return {"data": symbols, "count": count}


@router.get("/exchange/{exchange_id}", response_model=SymbolsPublic)
def read_symbols_by_exchange(
    exchange_id: int,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve symbols by exchange.
    """
    count_statement = (
        select(func.count()).select_from(Symbol).where(Symbol.exchange_id == exchange_id)
    )
    count = session.exec(count_statement).one()

    symbols = crud_symbol.get_symbols_by_exchange(
        session=session, exchange_id=exchange_id, skip=skip, limit=limit
    )

    return {"data": symbols, "count": count}


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=SymbolPublic,
)
def create_symbol(*, session: SessionDep, symbol_in: SymbolCreate) -> Any:
    """
    Create new symbol.
    """
    symbol = crud_symbol.get_symbol_by_exchange_and_code(
        session=session, exchange_id=symbol_in.exchange_id, symbol=symbol_in.symbol
    )
    if symbol:
        raise HTTPException(
            status_code=400,
            detail="The symbol with this exchange and code already exists in the system.",
        )

    symbol = crud_symbol.create_symbol(session=session, symbol_create=symbol_in)
    return symbol


@router.get("/{symbol_id}", response_model=SymbolPublic)
def read_symbol_by_id(
    symbol_id: int, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific symbol by id.
    """
    symbol = crud_symbol.get_symbol(session=session, symbol_id=symbol_id)
    if not symbol:
        raise HTTPException(status_code=404, detail="Symbol not found")
    return symbol


@router.patch(
    "/{symbol_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=SymbolPublic,
)
def update_symbol(
    *,
    session: SessionDep,
    symbol_id: int,
    symbol_in: SymbolUpdate,
) -> Any:
    """
    Update a symbol.
    """
    db_symbol = crud_symbol.get_symbol(session=session, symbol_id=symbol_id)
    if not db_symbol:
        raise HTTPException(
            status_code=404,
            detail="The symbol with this id does not exist in the system",
        )

    if symbol_in.exchange_id and symbol_in.symbol:
        existing_symbol = crud_symbol.get_symbol_by_exchange_and_code(
            session=session,
            exchange_id=symbol_in.exchange_id,
            symbol=symbol_in.symbol,
        )
        if existing_symbol and existing_symbol.id != symbol_id:
            raise HTTPException(
                status_code=409, detail="Symbol with this exchange and code already exists"
            )

    db_symbol = crud_symbol.update_symbol(
        session=session, db_symbol=db_symbol, symbol_in=symbol_in
    )
    return db_symbol


@router.delete("/{symbol_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_symbol(session: SessionDep, symbol_id: int) -> Message:
    """
    Delete a symbol.
    """
    symbol = crud_symbol.get_symbol(session=session, symbol_id=symbol_id)
    if not symbol:
        raise HTTPException(status_code=404, detail="Symbol not found")

    success = crud_symbol.delete_symbol(session=session, symbol_id=symbol_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete symbol")

    return Message(message="Symbol deleted successfully")
