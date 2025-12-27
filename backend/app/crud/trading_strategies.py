"""
CRUD operations for Trading Strategies
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlmodel import Session, select

from app.models.trading_strategies import (
    StrategySymbol,
    StrategySymbolCreate,
    StrategySymbolUpdate,
    TradingStrategy,
    TradingStrategyCreate,
    TradingStrategyUpdate,
)


# TradingStrategy CRUD
def create_trading_strategy(
    *, session: Session, user_id: uuid.UUID, strategy_create: TradingStrategyCreate
) -> TradingStrategy:
    """
    Create a new trading strategy for a user.

    Args:
        session: Database session
        user_id: User ID
        strategy_create: Trading strategy data

    Returns:
        Created TradingStrategy instance
    """
    db_obj = TradingStrategy(
        user_id=user_id,
        name=strategy_create.name,
        strategy_type=strategy_create.strategy_type,
        description=strategy_create.description,
        config=strategy_create.config,
        is_active=strategy_create.is_active,
    )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_trading_strategy(
    *, session: Session, strategy_id: int
) -> TradingStrategy | None:
    """
    Get a trading strategy by ID.

    Args:
        session: Database session
        strategy_id: Trading strategy ID

    Returns:
        TradingStrategy instance or None if not found
    """
    statement = select(TradingStrategy).where(TradingStrategy.id == strategy_id)
    return session.exec(statement).first()


def get_trading_strategies(
    *, session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[TradingStrategy]:
    """
    Get all trading strategies for a user.

    Args:
        session: Database session
        user_id: User ID
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return

    Returns:
        List of TradingStrategy instances
    """
    statement = (
        select(TradingStrategy)
        .where(TradingStrategy.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .order_by(TradingStrategy.created_at.desc())
    )
    return list(session.exec(statement).all())


def get_active_trading_strategies(
    *, session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[TradingStrategy]:
    """
    Get active trading strategies for a user.

    Args:
        session: Database session
        user_id: User ID
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return

    Returns:
        List of active TradingStrategy instances
    """
    statement = (
        select(TradingStrategy)
        .where(TradingStrategy.user_id == user_id, TradingStrategy.is_active == True)
        .offset(skip)
        .limit(limit)
        .order_by(TradingStrategy.created_at.desc())
    )
    return list(session.exec(statement).all())


def get_trading_strategies_by_type(
    *,
    session: Session,
    user_id: uuid.UUID,
    strategy_type: str,
    skip: int = 0,
    limit: int = 100,
) -> list[TradingStrategy]:
    """
    Get trading strategies by type for a user.

    Args:
        session: Database session
        user_id: User ID
        strategy_type: Strategy type (e.g., 'GRID', 'REBALANCING', 'DCA')
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return

    Returns:
        List of TradingStrategy instances
    """
    statement = (
        select(TradingStrategy)
        .where(
            TradingStrategy.user_id == user_id,
            TradingStrategy.strategy_type == strategy_type,
        )
        .offset(skip)
        .limit(limit)
        .order_by(TradingStrategy.created_at.desc())
    )
    return list(session.exec(statement).all())


def update_trading_strategy(
    *,
    session: Session,
    db_strategy: TradingStrategy,
    strategy_in: TradingStrategyUpdate,
) -> Any:
    """
    Update a trading strategy.

    Args:
        session: Database session
        db_strategy: Existing TradingStrategy instance
        strategy_in: Update data

    Returns:
        Updated TradingStrategy instance
    """
    strategy_data = strategy_in.model_dump(exclude_unset=True)

    # Update timestamp
    strategy_data["updated_at"] = datetime.now(timezone.utc)

    db_strategy.sqlmodel_update(strategy_data)
    session.add(db_strategy)
    session.commit()
    session.refresh(db_strategy)
    return db_strategy


def delete_trading_strategy(*, session: Session, strategy_id: int) -> bool:
    """
    Delete a trading strategy.

    Args:
        session: Database session
        strategy_id: Trading strategy ID

    Returns:
        True if deleted, False if not found
    """
    strategy = get_trading_strategy(session=session, strategy_id=strategy_id)
    if strategy:
        session.delete(strategy)
        session.commit()
        return True
    return False


def deactivate_trading_strategy(
    *, session: Session, strategy_id: int
) -> TradingStrategy | None:
    """
    Deactivate a trading strategy (soft delete).

    Args:
        session: Database session
        strategy_id: Trading strategy ID

    Returns:
        Updated TradingStrategy instance or None if not found
    """
    strategy = get_trading_strategy(session=session, strategy_id=strategy_id)
    if strategy:
        strategy.is_active = False
        strategy.updated_at = datetime.now(timezone.utc)

        session.add(strategy)
        session.commit()
        session.refresh(strategy)
        return strategy
    return None


# StrategySymbol CRUD
def create_strategy_symbol(
    *, session: Session, strategy_symbol_create: StrategySymbolCreate
) -> StrategySymbol:
    """
    Create a strategy-symbol mapping.

    Args:
        session: Database session
        strategy_symbol_create: Strategy symbol data

    Returns:
        Created StrategySymbol instance
    """
    db_obj = StrategySymbol.model_validate(strategy_symbol_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_strategy_symbol(
    *, session: Session, strategy_symbol_id: int
) -> StrategySymbol | None:
    """
    Get a strategy-symbol mapping by ID.

    Args:
        session: Database session
        strategy_symbol_id: Strategy symbol ID

    Returns:
        StrategySymbol instance or None if not found
    """
    statement = select(StrategySymbol).where(StrategySymbol.id == strategy_symbol_id)
    return session.exec(statement).first()


def get_strategy_symbol_by_ids(
    *, session: Session, strategy_id: int, symbol_id: int
) -> StrategySymbol | None:
    """
    Get a strategy-symbol mapping by strategy and symbol IDs.

    Args:
        session: Database session
        strategy_id: Strategy ID
        symbol_id: Symbol ID

    Returns:
        StrategySymbol instance or None if not found
    """
    statement = select(StrategySymbol).where(
        StrategySymbol.strategy_id == strategy_id, StrategySymbol.symbol_id == symbol_id
    )
    return session.exec(statement).first()


def get_strategy_symbols(
    *, session: Session, strategy_id: int, skip: int = 0, limit: int = 100
) -> list[StrategySymbol]:
    """
    Get all symbols for a strategy.

    Args:
        session: Database session
        strategy_id: Strategy ID
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return

    Returns:
        List of StrategySymbol instances
    """
    statement = (
        select(StrategySymbol)
        .where(StrategySymbol.strategy_id == strategy_id)
        .offset(skip)
        .limit(limit)
        .order_by(StrategySymbol.created_at.desc())
    )
    return list(session.exec(statement).all())


def get_active_strategy_symbols(
    *, session: Session, strategy_id: int, skip: int = 0, limit: int = 100
) -> list[StrategySymbol]:
    """
    Get active symbols for a strategy.

    Args:
        session: Database session
        strategy_id: Strategy ID
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return

    Returns:
        List of active StrategySymbol instances
    """
    statement = (
        select(StrategySymbol)
        .where(
            StrategySymbol.strategy_id == strategy_id, StrategySymbol.is_active == True
        )
        .offset(skip)
        .limit(limit)
        .order_by(StrategySymbol.created_at.desc())
    )
    return list(session.exec(statement).all())


def update_strategy_symbol(
    *,
    session: Session,
    db_strategy_symbol: StrategySymbol,
    strategy_symbol_in: StrategySymbolUpdate,
) -> Any:
    """
    Update a strategy-symbol mapping.

    Args:
        session: Database session
        db_strategy_symbol: Existing StrategySymbol instance
        strategy_symbol_in: Update data

    Returns:
        Updated StrategySymbol instance
    """
    strategy_symbol_data = strategy_symbol_in.model_dump(exclude_unset=True)
    db_strategy_symbol.sqlmodel_update(strategy_symbol_data)
    session.add(db_strategy_symbol)
    session.commit()
    session.refresh(db_strategy_symbol)
    return db_strategy_symbol


def delete_strategy_symbol(*, session: Session, strategy_symbol_id: int) -> bool:
    """
    Delete a strategy-symbol mapping.

    Args:
        session: Database session
        strategy_symbol_id: Strategy symbol ID

    Returns:
        True if deleted, False if not found
    """
    strategy_symbol = get_strategy_symbol(
        session=session, strategy_symbol_id=strategy_symbol_id
    )
    if strategy_symbol:
        session.delete(strategy_symbol)
        session.commit()
        return True
    return False
