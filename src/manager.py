from datetime import date
from typing import List, Dict
from .data_models import PriceSeries
from .sources.sources_base import BaseSource


class DataManager:
    """
    Orquestador que sabe hablar con múltiples fuentes de datos.
    """

    def __init__(self, sources: Dict[str, BaseSource]):
        """
        sources: dict del tipo {
            "yahoo": YahooSource(),
            "ibkr": IBKRSource(),
            "fred": FREDSource(api_key="..."),
        }
        """
        self.sources = sources

    def fetch_from_source(
        self,
        source_name: str,
        symbols: List[str],
        start: date,
        end: date,
        asset_type: str,
    ) -> List[PriceSeries]:
        src = self.sources[source_name]
        return src.get_price_history(symbols, start, end, asset_type)

    def fetch_multiple_sources(
        self,
        requests_list: List[Dict],
    ) -> List[PriceSeries]:
        """
        requests_list es una lista de diccionarios como:
        {
            "source": "yahoo" / "ibkr" / "fred",
            "symbols": ["AAPL","MSFT"],
            "start": date(...),
            "end": date(...),
            "asset_type": "stock"/"index"/"macro"
        }

        Devuelve todas las PriceSeries concatenadas.
        """
        all_series: List[PriceSeries] = []
        for req in requests_list:
            src_name    = req["source"]
            src_symbols = req["symbols"]
            src_start   = req["start"]
            src_end     = req["end"]
            src_type    = req["asset_type"]

            series_list = self.fetch_from_source(
                src_name,
                src_symbols,
                src_start,
                src_end,
                src_type,
            )
            all_series.extend(series_list)

        return all_series
