"""
API routes for Trading Strategies management
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.crud import trading_strategies as crud_strategy
from app.models.trading_strategies import (
    StrategySymbol,
    StrategySymbolCreate,
    StrategySymbolPublic,
    StrategySymbolsPublic,
    StrategySymbolUpdate,
    TradingStrategy,
    TradingStrategyCreate,
    TradingStrategyPublic,
    TradingStrategiesPublic,
    TradingStrategyUpdate,
)
from app.models.users import Message

router = APIRouter(prefix="/trading-strategies", tags=["trading-strategies"])


# Trading Strategy endpoints
@router.get("/", response_model=TradingStrategiesPublic)
def read_trading_strategies(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
    strategy_type: str | None = None,
) -> Any:
    """
    Retrieve current user's trading strategies.

    Query parameters:
    - is_active: Filter by active status (optional)
    - strategy_type: Filter by strategy type (optional)
    """
    # Build count statement
    count_statement = select(func.count()).select_from(TradingStrategy).where(
        TradingStrategy.user_id == current_user.id
    )

    if is_active is not None:
        count_statement = count_statement.where(TradingStrategy.is_active == is_active)

    if strategy_type:
        count_statement = count_statement.where(
            TradingStrategy.strategy_type == strategy_type.upper()
        )

    count = session.exec(count_statement).one()

    # Get strategies based on filters
    if is_active is not None and is_active:
        strategies = crud_strategy.get_active_trading_strategies(
            session=session, user_id=current_user.id, skip=skip, limit=limit
        )
    elif strategy_type:
        strategies = crud_strategy.get_trading_strategies_by_type(
            session=session,
            user_id=current_user.id,
            strategy_type=strategy_type.upper(),
            skip=skip,
            limit=limit,
        )
    else:
        strategies = crud_strategy.get_trading_strategies(
            session=session, user_id=current_user.id, skip=skip, limit=limit
        )

    return {"data": strategies, "count": count}


@router.post("/", response_model=TradingStrategyPublic)
def create_trading_strategy(
    *, session: SessionDep, current_user: CurrentUser, strategy_in: TradingStrategyCreate
) -> Any:
    """
    Create a new trading strategy for the current user.

    Request body example:
    ```json
    {
        "name": "My Grid Trading Strategy",
        "strategy_type": "GRID",
        "description": "Grid trading for BTC",
        "config": {
            "grid_count": 10,
            "price_range": [50000, 60000],
            "investment_amount": 1000000
        },
        "is_active": false
    }
    ```
    """
    # Normalize strategy type to uppercase
    strategy_in.strategy_type = strategy_in.strategy_type.upper()

    strategy = crud_strategy.create_trading_strategy(
        session=session, user_id=current_user.id, strategy_create=strategy_in
    )

    return strategy


@router.get("/{strategy_id}", response_model=TradingStrategyPublic)
def read_trading_strategy_by_id(
    strategy_id: int, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific trading strategy by ID.

    Only the owner can access their own strategies.
    """
    strategy = crud_strategy.get_trading_strategy(
        session=session, strategy_id=strategy_id
    )

    if not strategy:
        raise HTTPException(status_code=404, detail="Trading strategy not found")

    # Check ownership
    if strategy.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this trading strategy"
        )

    return strategy


@router.patch("/{strategy_id}", response_model=TradingStrategyPublic)
def update_trading_strategy(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    strategy_id: int,
    strategy_in: TradingStrategyUpdate,
) -> Any:
    """
    Update a trading strategy.

    Can update:
    - name
    - strategy_type
    - description
    - config (strategy configuration)
    - is_active
    """
    db_strategy = crud_strategy.get_trading_strategy(
        session=session, strategy_id=strategy_id
    )

    if not db_strategy:
        raise HTTPException(
            status_code=404,
            detail="The trading strategy with this id does not exist in the system",
        )

    # Check ownership
    if db_strategy.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to modify this trading strategy"
        )

    # Normalize strategy type to uppercase if provided
    if strategy_in.strategy_type:
        strategy_in.strategy_type = strategy_in.strategy_type.upper()

    db_strategy = crud_strategy.update_trading_strategy(
        session=session, db_strategy=db_strategy, strategy_in=strategy_in
    )

    return db_strategy


@router.post("/{strategy_id}/deactivate", response_model=TradingStrategyPublic)
def deactivate_trading_strategy(
    strategy_id: int, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Deactivate a trading strategy (soft delete).

    Deactivated strategies are kept in the database but will not execute.
    """
    db_strategy = crud_strategy.get_trading_strategy(
        session=session, strategy_id=strategy_id
    )

    if not db_strategy:
        raise HTTPException(status_code=404, detail="Trading strategy not found")

    # Check ownership
    if db_strategy.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to deactivate this trading strategy"
        )

    if not db_strategy.is_active:
        raise HTTPException(
            status_code=400, detail="Trading strategy is already deactivated"
        )

    deactivated_strategy = crud_strategy.deactivate_trading_strategy(
        session=session, strategy_id=strategy_id
    )

    if not deactivated_strategy:
        raise HTTPException(
            status_code=500, detail="Failed to deactivate trading strategy"
        )

    return deactivated_strategy


@router.delete("/{strategy_id}")
def delete_trading_strategy(
    strategy_id: int, session: SessionDep, current_user: CurrentUser
) -> Message:
    """
    Permanently delete a trading strategy.

    WARNING: This action cannot be undone.
    This will also delete all associated strategy-symbol mappings.
    Consider using the deactivate endpoint instead.
    """
    db_strategy = crud_strategy.get_trading_strategy(
        session=session, strategy_id=strategy_id
    )

    if not db_strategy:
        raise HTTPException(status_code=404, detail="Trading strategy not found")

    # Check ownership
    if db_strategy.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this trading strategy"
        )

    success = crud_strategy.delete_trading_strategy(
        session=session, strategy_id=strategy_id
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete trading strategy")

    return Message(message="Trading strategy deleted successfully")


# Strategy Symbol endpoints
@router.get("/{strategy_id}/symbols", response_model=StrategySymbolsPublic)
def read_strategy_symbols(
    strategy_id: int,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
) -> Any:
    """
    Retrieve symbols for a specific trading strategy.

    Query parameters:
    - is_active: Filter by active status (optional)
    """
    # First verify strategy ownership
    strategy = crud_strategy.get_trading_strategy(
        session=session, strategy_id=strategy_id
    )

    if not strategy:
        raise HTTPException(status_code=404, detail="Trading strategy not found")

    if strategy.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this trading strategy"
        )

    # Build count statement
    count_statement = select(func.count()).select_from(StrategySymbol).where(
        StrategySymbol.strategy_id == strategy_id
    )

    if is_active is not None:
        count_statement = count_statement.where(StrategySymbol.is_active == is_active)

    count = session.exec(count_statement).one()

    # Get symbols based on filters
    if is_active is not None and is_active:
        symbols = crud_strategy.get_active_strategy_symbols(
            session=session, strategy_id=strategy_id, skip=skip, limit=limit
        )
    else:
        symbols = crud_strategy.get_strategy_symbols(
            session=session, strategy_id=strategy_id, skip=skip, limit=limit
        )

    return {"data": symbols, "count": count}


@router.post("/{strategy_id}/symbols", response_model=StrategySymbolPublic)
def create_strategy_symbol(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    strategy_id: int,
    strategy_symbol_in: StrategySymbolCreate,
) -> Any:
    """
    Add a symbol to a trading strategy.

    Request body example:
    ```json
    {
        "strategy_id": 1,
        "symbol_id": 123,
        "allocation_ratio": 0.25,
        "is_active": true
    }
    ```

    Note: allocation_ratio should be between 0.0 and 1.0
    """
    # Verify strategy ownership
    strategy = crud_strategy.get_trading_strategy(
        session=session, strategy_id=strategy_id
    )

    if not strategy:
        raise HTTPException(status_code=404, detail="Trading strategy not found")

    if strategy.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to modify this trading strategy"
        )

    # Ensure strategy_id in path matches body
    if strategy_symbol_in.strategy_id != strategy_id:
        raise HTTPException(
            status_code=400,
            detail="Strategy ID in path must match strategy_id in request body",
        )

    # Check if symbol already exists for this strategy
    existing_symbol = crud_strategy.get_strategy_symbol_by_ids(
        session=session,
        strategy_id=strategy_id,
        symbol_id=strategy_symbol_in.symbol_id,
    )

    if existing_symbol:
        raise HTTPException(
            status_code=400,
            detail="This symbol is already added to the strategy",
        )

    # Validate allocation ratio
    if not (0.0 <= strategy_symbol_in.allocation_ratio <= 1.0):
        raise HTTPException(
            status_code=400,
            detail="Allocation ratio must be between 0.0 and 1.0",
        )

    strategy_symbol = crud_strategy.create_strategy_symbol(
        session=session, strategy_symbol_create=strategy_symbol_in
    )

    return strategy_symbol


@router.patch("/{strategy_id}/symbols/{symbol_id}", response_model=StrategySymbolPublic)
def update_strategy_symbol(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    strategy_id: int,
    symbol_id: int,
    strategy_symbol_in: StrategySymbolUpdate,
) -> Any:
    """
    Update a strategy-symbol mapping.

    Can update:
    - allocation_ratio
    - is_active
    """
    # Verify strategy ownership
    strategy = crud_strategy.get_trading_strategy(
        session=session, strategy_id=strategy_id
    )

    if not strategy:
        raise HTTPException(status_code=404, detail="Trading strategy not found")

    if strategy.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to modify this trading strategy"
        )

    # Get strategy symbol mapping
    db_strategy_symbol = crud_strategy.get_strategy_symbol_by_ids(
        session=session, strategy_id=strategy_id, symbol_id=symbol_id
    )

    if not db_strategy_symbol:
        raise HTTPException(
            status_code=404,
            detail="Symbol not found in this strategy",
        )

    # Validate allocation ratio if provided
    if (
        strategy_symbol_in.allocation_ratio is not None
        and not (0.0 <= strategy_symbol_in.allocation_ratio <= 1.0)
    ):
        raise HTTPException(
            status_code=400,
            detail="Allocation ratio must be between 0.0 and 1.0",
        )

    db_strategy_symbol = crud_strategy.update_strategy_symbol(
        session=session,
        db_strategy_symbol=db_strategy_symbol,
        strategy_symbol_in=strategy_symbol_in,
    )

    return db_strategy_symbol


@router.delete("/{strategy_id}/symbols/{symbol_id}")
def delete_strategy_symbol(
    strategy_id: int, symbol_id: int, session: SessionDep, current_user: CurrentUser
) -> Message:
    """
    Remove a symbol from a trading strategy.
    """
    # Verify strategy ownership
    strategy = crud_strategy.get_trading_strategy(
        session=session, strategy_id=strategy_id
    )

    if not strategy:
        raise HTTPException(status_code=404, detail="Trading strategy not found")

    if strategy.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to modify this trading strategy"
        )

    # Get strategy symbol mapping
    db_strategy_symbol = crud_strategy.get_strategy_symbol_by_ids(
        session=session, strategy_id=strategy_id, symbol_id=symbol_id
    )

    if not db_strategy_symbol:
        raise HTTPException(
            status_code=404,
            detail="Symbol not found in this strategy",
        )

    success = crud_strategy.delete_strategy_symbol(
        session=session, strategy_symbol_id=db_strategy_symbol.id
    )

    if not success:
        raise HTTPException(
            status_code=500, detail="Failed to remove symbol from strategy"
        )

    return Message(message="Symbol removed from strategy successfully")
