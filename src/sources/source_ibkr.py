from datetime import date, timedelta
from typing import List

from .sources_base import BaseSource
from ..data_models import PriceSeries, PricePoint


class IBKRSource(BaseSource):
    """
    Simulación de Interactive Brokers.
    Esto muestra cómo integraríamos un broker real.

    Generamos datos sintéticos pero en el mismo formato estándar.
    """

    def get_price_history(
        self,
        symbols: List[str],
        start: date,
        end: date,
        asset_type: str,
    ) -> List[PriceSeries]:

        results: List[PriceSeries] = []

        for sym in symbols:
            pts: List[PricePoint] = []
            current = start
            price = 100.0  # precio inicial inventado

            while current <= end:
                open_p = price
                high_p = price * 1.01
                low_p = price * 0.99
                close_p = price * 1.005
                vol_p = 1_000_000.0

                pts.append(
                    PricePoint(
                        date=current,
                        open=open_p,
                        high=high_p,
                        low=low_p,
                        close=close_p,
                        volume=vol_p,
                    )
                )

                price = close_p * 1.002
                current += timedelta(days=1)

            series = PriceSeries(
                symbol=sym,
                source="ibkr",
                asset_type=asset_type,
                currency="USD",
                data=pts,
            )
            results.append(series)

        return results
