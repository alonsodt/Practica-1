from abc import ABC, abstractmethod
from datetime import date
from typing import List
from ..data_models import PriceSeries


class BaseSource(ABC):
    """
    Interfaz que toda fuente debe implementar.
    """

    @abstractmethod
    def get_price_history(
        self,
        symbols: List[str],
        start: date,
        end: date,
        asset_type: str,
    ) -> List[PriceSeries]:
        """
        Devuelve una lista de PriceSeries (una por símbolo).
        """
        pass
