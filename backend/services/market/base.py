from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseMarketProvider(ABC):
    """Abstract Base Class for Market Intelligence Data Providers."""

    @abstractmethod
    def get_role_market_data(self, role_name: str) -> Optional[Dict[str, Any]]:
        """Returns market demand data dictionary for a specific role title."""
        pass

    @abstractmethod
    def get_all_market_data(self) -> Dict[str, Dict[str, Any]]:
        """Returns complete dictionary of all market roles."""
        pass
