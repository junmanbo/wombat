from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.crud import exchanges as crud_exchange
from app.models.exchanges import (
    Exchange,
    ExchangeCreate,
    ExchangePublic,
    ExchangesPublic,
    ExchangeUpdate,
)
from app.models.users import Message

router = APIRouter(prefix="/exchanges", tags=["exchanges"])


@router.get("/", response_model=ExchangesPublic)
def read_exchanges(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve exchanges.
    """
    count_statement = select(func.count()).select_from(Exchange)
    count = session.exec(count_statement).one()

    statement = select(Exchange).offset(skip).limit(limit)
    exchanges = session.exec(statement).all()

    return {"data": exchanges, "count": count}


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ExchangePublic,
)
def create_exchange(*, session: SessionDep, exchange_in: ExchangeCreate) -> Any:
    """
    Create new exchange.
    """
    exchange = crud_exchange.get_exchange_by_code(session=session, code=exchange_in.code)
    if exchange:
        raise HTTPException(
            status_code=400,
            detail="The exchange with this code already exists in the system.",
        )

    exchange = crud_exchange.create_exchange(session=session, exchange_create=exchange_in)
    return exchange


@router.get("/{exchange_id}", response_model=ExchangePublic)
def read_exchange_by_id(
    exchange_id: int, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific exchange by id.
    """
    exchange = crud_exchange.get_exchange(session=session, exchange_id=exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
    return exchange


@router.get("/code/{code}", response_model=ExchangePublic)
def read_exchange_by_code(
    code: str, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific exchange by code.
    """
    exchange = crud_exchange.get_exchange_by_code(session=session, code=code)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
    return exchange


@router.patch(
    "/{exchange_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ExchangePublic,
)
def update_exchange(
    *,
    session: SessionDep,
    exchange_id: int,
    exchange_in: ExchangeUpdate,
) -> Any:
    """
    Update an exchange.
    """
    db_exchange = crud_exchange.get_exchange(session=session, exchange_id=exchange_id)
    if not db_exchange:
        raise HTTPException(
            status_code=404,
            detail="The exchange with this id does not exist in the system",
        )

    if exchange_in.code:
        existing_exchange = crud_exchange.get_exchange_by_code(
            session=session, code=exchange_in.code
        )
        if existing_exchange and existing_exchange.id != exchange_id:
            raise HTTPException(
                status_code=409, detail="Exchange with this code already exists"
            )

    db_exchange = crud_exchange.update_exchange(
        session=session, db_exchange=db_exchange, exchange_in=exchange_in
    )
    return db_exchange


@router.delete(
    "/{exchange_id}", dependencies=[Depends(get_current_active_superuser)]
)
def delete_exchange(session: SessionDep, exchange_id: int) -> Message:
    """
    Delete an exchange.
    """
    exchange = crud_exchange.get_exchange(session=session, exchange_id=exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")

    success = crud_exchange.delete_exchange(session=session, exchange_id=exchange_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete exchange")

    return Message(message="Exchange deleted successfully")