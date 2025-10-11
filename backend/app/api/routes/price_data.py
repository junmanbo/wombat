from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.crud import price_data as crud_price_data
from app.crud import symbols as crud_symbol
from app.models.price_data import (
    PriceData,
    PriceDataCreate,
    PriceDataListPublic,
    PriceDataPublic,
    PriceDataUpdate,
)
from app.models.users import Message

router = APIRouter(prefix="/price-data", tags=["price-data"])


@router.get("/symbol/{symbol_id}", response_model=PriceDataListPublic)
def read_price_data_by_symbol(
    symbol_id: int,
    session: SessionDep,
    current_user: CurrentUser,
    timeframe: str = Query(..., description="시간 프레임 (예: 1d, 1h, 5m)"),
    start_time: datetime | None = Query(
        None, description="시작 시간 (ISO 8601 형식)"
    ),
    end_time: datetime | None = Query(None, description="종료 시간 (ISO 8601 형식)"),
    skip: int = 0,
    limit: int = Query(default=100, le=1000),
) -> Any:
    """
    특정 종목의 가격 데이터 조회

    시간 범위를 지정하여 필터링 가능
    """
    # 종목 존재 확인
    symbol = crud_symbol.get_symbol(session=session, symbol_id=symbol_id)
    if not symbol:
        raise HTTPException(status_code=404, detail="Symbol not found")

    # 조건에 맞는 전체 개수 조회
    count_statement = select(func.count()).select_from(PriceData).where(
        PriceData.symbol_id == symbol_id, PriceData.timeframe == timeframe
    )
    if start_time:
        count_statement = count_statement.where(PriceData.timestamp >= start_time)
    if end_time:
        count_statement = count_statement.where(PriceData.timestamp <= end_time)

    count = session.exec(count_statement).one()

    # 가격 데이터 조회
    price_data_list = crud_price_data.get_price_data_by_symbol(
        session=session,
        symbol_id=symbol_id,
        timeframe=timeframe,
        start_time=start_time,
        end_time=end_time,
        skip=skip,
        limit=limit,
    )

    return {"data": price_data_list, "count": count}


@router.get("/symbol/{symbol_id}/latest", response_model=PriceDataPublic)
def read_latest_price_data(
    symbol_id: int,
    session: SessionDep,
    current_user: CurrentUser,
    timeframe: str = Query(..., description="시간 프레임 (예: 1d, 1h, 5m)"),
) -> Any:
    """
    특정 종목의 가장 최신 가격 데이터 조회
    """
    # 종목 존재 확인
    symbol = crud_symbol.get_symbol(session=session, symbol_id=symbol_id)
    if not symbol:
        raise HTTPException(status_code=404, detail="Symbol not found")

    price_data = crud_price_data.get_latest_price_data(
        session=session, symbol_id=symbol_id, timeframe=timeframe
    )

    if not price_data:
        raise HTTPException(
            status_code=404,
            detail=f"No price data found for symbol_id={symbol_id}, timeframe={timeframe}",
        )

    return price_data


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=PriceDataPublic,
)
def create_price_data(*, session: SessionDep, price_data_in: PriceDataCreate) -> Any:
    """
    새로운 가격 데이터 생성
    """
    # 종목 존재 확인
    symbol = crud_symbol.get_symbol(session=session, symbol_id=price_data_in.symbol_id)
    if not symbol:
        raise HTTPException(status_code=404, detail="Symbol not found")

    # 중복 확인
    existing = crud_price_data.get_price_data_by_timestamp(
        session=session,
        symbol_id=price_data_in.symbol_id,
        timestamp=price_data_in.timestamp,
        timeframe=price_data_in.timeframe,
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Price data with this symbol_id, timestamp, and timeframe already exists",
        )

    price_data = crud_price_data.create_price_data(
        session=session, price_data_create=price_data_in
    )
    return price_data


@router.post(
    "/bulk",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=PriceDataListPublic,
)
def bulk_create_price_data(
    *, session: SessionDep, price_data_list: list[PriceDataCreate]
) -> Any:
    """
    가격 데이터 대량 생성

    중복된 데이터는 자동으로 스킵됩니다 (unique constraint 위반 방지)
    """
    if not price_data_list:
        raise HTTPException(status_code=400, detail="Empty price data list")

    # 모든 symbol_id 존재 확인
    symbol_ids = {item.symbol_id for item in price_data_list}
    for symbol_id in symbol_ids:
        symbol = crud_symbol.get_symbol(session=session, symbol_id=symbol_id)
        if not symbol:
            raise HTTPException(
                status_code=404, detail=f"Symbol with id={symbol_id} not found"
            )

    # 중복 제거: 기존 데이터 필터링
    filtered_list = []
    for item in price_data_list:
        existing = crud_price_data.get_price_data_by_timestamp(
            session=session,
            symbol_id=item.symbol_id,
            timestamp=item.timestamp,
            timeframe=item.timeframe,
        )
        if not existing:
            filtered_list.append(item)

    if not filtered_list:
        return {"data": [], "count": 0}

    # 대량 삽입
    created_data = crud_price_data.bulk_create_price_data(
        session=session, price_data_list=filtered_list
    )

    return {"data": created_data, "count": len(created_data)}


@router.get("/{price_data_id}", response_model=PriceDataPublic)
def read_price_data_by_id(
    price_data_id: int, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    ID로 가격 데이터 조회
    """
    price_data = crud_price_data.get_price_data(
        session=session, price_data_id=price_data_id
    )
    if not price_data:
        raise HTTPException(status_code=404, detail="Price data not found")
    return price_data


@router.patch(
    "/{price_data_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=PriceDataPublic,
)
def update_price_data(
    *,
    session: SessionDep,
    price_data_id: int,
    price_data_in: PriceDataUpdate,
) -> Any:
    """
    가격 데이터 업데이트

    주의: 일반적으로 가격 데이터는 불변이므로 이 API는 신중하게 사용해야 합니다
    """
    db_price_data = crud_price_data.get_price_data(
        session=session, price_data_id=price_data_id
    )
    if not db_price_data:
        raise HTTPException(
            status_code=404,
            detail="The price data with this id does not exist in the system",
        )

    # symbol_id가 변경되는 경우 해당 symbol 존재 확인
    if price_data_in.symbol_id and price_data_in.symbol_id != db_price_data.symbol_id:
        symbol = crud_symbol.get_symbol(
            session=session, symbol_id=price_data_in.symbol_id
        )
        if not symbol:
            raise HTTPException(status_code=404, detail="Symbol not found")

    # unique constraint 위반 확인
    if (
        price_data_in.symbol_id
        or price_data_in.timestamp
        or price_data_in.timeframe
    ):
        check_symbol_id = price_data_in.symbol_id or db_price_data.symbol_id
        check_timestamp = price_data_in.timestamp or db_price_data.timestamp
        check_timeframe = price_data_in.timeframe or db_price_data.timeframe

        existing = crud_price_data.get_price_data_by_timestamp(
            session=session,
            symbol_id=check_symbol_id,
            timestamp=check_timestamp,
            timeframe=check_timeframe,
        )
        if existing and existing.id != price_data_id:
            raise HTTPException(
                status_code=409,
                detail="Price data with this symbol_id, timestamp, and timeframe already exists",
            )

    db_price_data = crud_price_data.update_price_data(
        session=session, db_price_data=db_price_data, price_data_in=price_data_in
    )
    return db_price_data


@router.delete(
    "/{price_data_id}", dependencies=[Depends(get_current_active_superuser)]
)
def delete_price_data(session: SessionDep, price_data_id: int) -> Message:
    """
    가격 데이터 삭제
    """
    price_data = crud_price_data.get_price_data(
        session=session, price_data_id=price_data_id
    )
    if not price_data:
        raise HTTPException(status_code=404, detail="Price data not found")

    success = crud_price_data.delete_price_data(
        session=session, price_data_id=price_data_id
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete price data")

    return Message(message="Price data deleted successfully")


@router.delete(
    "/symbol/{symbol_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_price_data_by_symbol(
    symbol_id: int,
    session: SessionDep,
    timeframe: str | None = Query(
        None, description="특정 timeframe만 삭제 (지정 안하면 모든 timeframe 삭제)"
    ),
) -> Message:
    """
    특정 종목의 가격 데이터 삭제

    timeframe을 지정하지 않으면 해당 종목의 모든 가격 데이터를 삭제합니다
    """
    # 종목 존재 확인
    symbol = crud_symbol.get_symbol(session=session, symbol_id=symbol_id)
    if not symbol:
        raise HTTPException(status_code=404, detail="Symbol not found")

    deleted_count = crud_price_data.delete_price_data_by_symbol(
        session=session, symbol_id=symbol_id, timeframe=timeframe
    )

    return Message(
        message=f"Deleted {deleted_count} price data records for symbol_id={symbol_id}"
    )
