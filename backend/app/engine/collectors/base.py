"""
Base Collector Class

Provides a common interface for all data collectors.
"""

from abc import ABC, abstractmethod
from typing import Any

from sqlmodel import Session


class BaseCollector(ABC):
    """Base class for all data collectors."""

    def __init__(self, session: Session):
        """
        Initialize the collector.

        Args:
            session: Database session for data persistence
        """
        self.session = session

    @abstractmethod
    async def fetch_symbols(self) -> list[dict[str, Any]]:
        """
        Fetch symbols from the exchange.

        Returns:
            List of symbol data dictionaries
        """
        pass

    @abstractmethod
    async def save_symbols(self, symbols_data: list[dict[str, Any]]) -> int:
        """
        Save symbols to the database.

        Args:
            symbols_data: List of symbol data dictionaries

        Returns:
            Number of symbols saved
        """
        pass

    async def collect_and_save(self) -> int:
        """
        Fetch and save symbols in one operation.

        Returns:
            Number of symbols saved
        """
        symbols_data = await self.fetch_symbols()
        return await self.save_symbols(symbols_data)
