from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.crud import realtime_price as crud_realtime_price
from app.crud import symbols as crud_symbol
from app.models.realtime_price import (
    RealtimePrice,
    RealtimePriceCreate,
    RealtimePriceListPublic,
    RealtimePricePublic,
    RealtimePriceUpdate,
)
from app.models.users import Message

router = APIRouter(prefix="/realtime-price", tags=["realtime-price"])


@router.get("/", response_model=RealtimePriceListPublic)
def read_realtime_prices(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = Query(default=100, le=1000),
) -> Any:
    """
    모든 실시간 가격 데이터 조회 (페이지네이션)
    """
    # 전체 개수 조회
    count_statement = select(func.count()).select_from(RealtimePrice)
    count = session.exec(count_statement).one()

    # 실시간 가격 데이터 조회
    realtime_prices = crud_realtime_price.get_realtime_prices(
        session=session, skip=skip, limit=limit
    )

    return {"data": realtime_prices, "count": count}


@router.get("/symbol/{symbol_id}", response_model=RealtimePricePublic)
def read_realtime_price_by_symbol(
    symbol_id: int,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    특정 종목의 실시간 가격 데이터 조회
    """
    # 종목 존재 확인
    symbol = crud_symbol.get_symbol(session=session, symbol_id=symbol_id)
    if not symbol:
        raise HTTPException(status_code=404, detail="Symbol not found")

    realtime_price = crud_realtime_price.get_realtime_price_by_symbol(
        session=session, symbol_id=symbol_id
    )

    if not realtime_price:
        raise HTTPException(
            status_code=404,
            detail=f"No realtime price data found for symbol_id={symbol_id}",
        )

    return realtime_price


@router.post("/symbols", response_model=RealtimePriceListPublic)
def read_realtime_prices_by_symbols(
    session: SessionDep,
    current_user: CurrentUser,
    symbol_ids: list[int],
) -> Any:
    """
    여러 종목의 실시간 가격 데이터 조회
    """
    if not symbol_ids:
        raise HTTPException(status_code=400, detail="Empty symbol_ids list")

    # 모든 symbol_id 존재 확인
    for symbol_id in symbol_ids:
        symbol = crud_symbol.get_symbol(session=session, symbol_id=symbol_id)
        if not symbol:
            raise HTTPException(
                status_code=404, detail=f"Symbol with id={symbol_id} not found"
            )

    realtime_prices = crud_realtime_price.get_realtime_prices_by_symbols(
        session=session, symbol_ids=symbol_ids
    )

    return {"data": realtime_prices, "count": len(realtime_prices)}


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=RealtimePricePublic,
)
def create_realtime_price(
    *, session: SessionDep, realtime_price_in: RealtimePriceCreate
) -> Any:
    """
    새로운 실시간 가격 데이터 생성
    """
    # 종목 존재 확인
    symbol = crud_symbol.get_symbol(
        session=session, symbol_id=realtime_price_in.symbol_id
    )
    if not symbol:
        raise HTTPException(status_code=404, detail="Symbol not found")

    # 중복 확인
    existing = crud_realtime_price.get_realtime_price_by_symbol(
        session=session, symbol_id=realtime_price_in.symbol_id
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Realtime price data for symbol_id={realtime_price_in.symbol_id} already exists. Use PATCH to update or POST /upsert to create or update.",
        )

    realtime_price = crud_realtime_price.create_realtime_price(
        session=session, realtime_price_create=realtime_price_in
    )
    return realtime_price


@router.post(
    "/upsert",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=RealtimePricePublic,
)
def upsert_realtime_price(
    *, session: SessionDep, realtime_price_in: RealtimePriceCreate
) -> Any:
    """
    실시간 가격 데이터 생성 또는 업데이트 (UPSERT)

    동일한 symbol_id가 존재하면 업데이트, 없으면 생성
    """
    # 종목 존재 확인
    symbol = crud_symbol.get_symbol(
        session=session, symbol_id=realtime_price_in.symbol_id
    )
    if not symbol:
        raise HTTPException(status_code=404, detail="Symbol not found")

    realtime_price = crud_realtime_price.upsert_realtime_price(
        session=session, realtime_price_create=realtime_price_in
    )
    return realtime_price


@router.post(
    "/bulk-upsert",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=RealtimePriceListPublic,
)
def bulk_upsert_realtime_prices(
    *, session: SessionDep, realtime_price_list: list[RealtimePriceCreate]
) -> Any:
    """
    실시간 가격 데이터 대량 생성/업데이트

    동일한 symbol_id가 존재하면 업데이트, 없으면 생성
    """
    if not realtime_price_list:
        raise HTTPException(status_code=400, detail="Empty realtime price list")

    # 모든 symbol_id 존재 확인
    symbol_ids = {item.symbol_id for item in realtime_price_list}
    for symbol_id in symbol_ids:
        symbol = crud_symbol.get_symbol(session=session, symbol_id=symbol_id)
        if not symbol:
            raise HTTPException(
                status_code=404, detail=f"Symbol with id={symbol_id} not found"
            )

    # 대량 UPSERT
    upserted_data = crud_realtime_price.bulk_upsert_realtime_prices(
        session=session, realtime_price_list=realtime_price_list
    )

    return {"data": upserted_data, "count": len(upserted_data)}


@router.get("/{realtime_price_id}", response_model=RealtimePricePublic)
def read_realtime_price_by_id(
    realtime_price_id: int, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    ID로 실시간 가격 데이터 조회
    """
    realtime_price = crud_realtime_price.get_realtime_price(
        session=session, realtime_price_id=realtime_price_id
    )
    if not realtime_price:
        raise HTTPException(status_code=404, detail="Realtime price data not found")
    return realtime_price


@router.patch(
    "/{realtime_price_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=RealtimePricePublic,
)
def update_realtime_price(
    *,
    session: SessionDep,
    realtime_price_id: int,
    realtime_price_in: RealtimePriceUpdate,
) -> Any:
    """
    실시간 가격 데이터 업데이트
    """
    db_realtime_price = crud_realtime_price.get_realtime_price(
        session=session, realtime_price_id=realtime_price_id
    )
    if not db_realtime_price:
        raise HTTPException(
            status_code=404,
            detail="The realtime price data with this id does not exist in the system",
        )

    # symbol_id가 변경되는 경우
    if (
        realtime_price_in.symbol_id
        and realtime_price_in.symbol_id != db_realtime_price.symbol_id
    ):
        # 새로운 symbol 존재 확인
        symbol = crud_symbol.get_symbol(
            session=session, symbol_id=realtime_price_in.symbol_id
        )
        if not symbol:
            raise HTTPException(status_code=404, detail="Symbol not found")

        # unique constraint 위반 확인
        existing = crud_realtime_price.get_realtime_price_by_symbol(
            session=session, symbol_id=realtime_price_in.symbol_id
        )
        if existing and existing.id != realtime_price_id:
            raise HTTPException(
                status_code=409,
                detail=f"Realtime price data for symbol_id={realtime_price_in.symbol_id} already exists",
            )

    db_realtime_price = crud_realtime_price.update_realtime_price(
        session=session,
        db_realtime_price=db_realtime_price,
        realtime_price_in=realtime_price_in,
    )
    return db_realtime_price


@router.delete(
    "/{realtime_price_id}", dependencies=[Depends(get_current_active_superuser)]
)
def delete_realtime_price(session: SessionDep, realtime_price_id: int) -> Message:
    """
    실시간 가격 데이터 삭제
    """
    realtime_price = crud_realtime_price.get_realtime_price(
        session=session, realtime_price_id=realtime_price_id
    )
    if not realtime_price:
        raise HTTPException(status_code=404, detail="Realtime price data not found")

    success = crud_realtime_price.delete_realtime_price(
        session=session, realtime_price_id=realtime_price_id
    )
    if not success:
        raise HTTPException(
            status_code=500, detail="Failed to delete realtime price data"
        )

    return Message(message="Realtime price data deleted successfully")


@router.delete(
    "/symbol/{symbol_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_realtime_price_by_symbol(symbol_id: int, session: SessionDep) -> Message:
    """
    특정 종목의 실시간 가격 데이터 삭제
    """
    # 종목 존재 확인
    symbol = crud_symbol.get_symbol(session=session, symbol_id=symbol_id)
    if not symbol:
        raise HTTPException(status_code=404, detail="Symbol not found")

    success = crud_realtime_price.delete_realtime_price_by_symbol(
        session=session, symbol_id=symbol_id
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"No realtime price data found for symbol_id={symbol_id}",
        )

    return Message(
        message=f"Deleted realtime price data for symbol_id={symbol_id} successfully"
    )
