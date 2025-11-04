# main.py

import os
import sys
import random
from datetime import date
from io import StringIO
import pandas as pd
import requests

# Aseguramos que se pueda importar el paquete src cuando ejecutas `python main.py`
sys.path.append(os.path.dirname(__file__))

from src.manager import DataManager
from src.sources.source_yahoo import YahooSource
from src.sources.source_ibkr import IBKRSource
from src.sources.source_fred import FREDSource
from src.portfolio import Portfolio


def get_random_sp500_symbols_from_finviz(n: int = 10) -> list[str]:
    """
    Descarga la lista de empresas del S&P 500 desde Finviz
    y devuelve `n` tickers elegidos al azar.
    """
    url = "https://finviz.com/screener.ashx?v=111&f=idx_sp500"
    headers = {"User-Agent": "Mozilla/5.0"}

    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()

    # StringIO para evitar el FutureWarning
    html_buffer = StringIO(resp.text)

    # Usamos el parser 'html5lib' para no depender de lxml
    tables = pd.read_html(html_buffer, flavor="html5lib")

    tickers = None
    for df in tables:
        if "Ticker" in df.columns:
            tickers = df["Ticker"].tolist()
            break

    if not tickers:
        raise ValueError("No se pudo encontrar la columna 'Ticker' en Finviz.")

    if n > len(tickers):
        n = len(tickers)

    return random.sample(tickers, k=n)

def pretty_preview(series_list, max_points: int = 3):
    """
    Muestra por consola un resumen sencillo de cada PriceSeries.
    """
    for s in series_list:
        print("=" * 60)
        print(f"Symbol:      {s.symbol}")
        print(f"Source:      {s.source}")
        print(f"Asset Type:  {s.asset_type}")
        print(f"Currency:    {s.currency}")
        print(f"mean_return: {s.mean_return}")
        print(f"stdev_ret.:  {s.stdev_return}")
        print(f"Puntos tot.: {len(s.data)}")
        print(f"Primeros {max_points} puntos:")
        for p in s.data[:max_points]:
            if s.asset_type == "macro":
                print(f"  {p.date} | Valor: {p.close}{s.currency}")
            else:
                print(
                    f"  {p.date} | "
                    f"O:{p.open} H:{p.high} L:{p.low} "
                    f"C:{p.close} V:{p.volume}"
                )


if __name__ == "__main__":
    # --------------------------------------------------
    # 1. Obtener N activos aleatorios del S&P 500 (desde Finviz)
    # --------------------------------------------------
    N_ASSETS = 10
    print(f"Obteniendo {N_ASSETS} tickers aleatorios del S&P 500 desde Finviz...")
    sp500_symbols = get_random_sp500_symbols_from_finviz(N_ASSETS)
    print("Tickers elegidos:", sp500_symbols)

    # --------------------------------------------------
    # 2. Crear fuentes (APIs) y el DataManager
    # --------------------------------------------------
    yahoo = YahooSource()
    ibkr = IBKRSource()
    fred = FREDSource(api_key=None)  # si tienes API key de FRED, ponla aquí

    manager = DataManager(
        sources={
            "yahoo": yahoo,
            "ibkr": ibkr,
            "fred": fred,
        }
    )

    # --------------------------------------------------
    # 3. Definir rango de fechas para histórico
    # --------------------------------------------------
    start_date = date(2024, 1, 1)
    end_date = date(2024, 12, 31)

    # --------------------------------------------------
    # 4. Pedir histórico de los N activos a Yahoo a través del DataManager
    # --------------------------------------------------
    requests_list = [
        {
            "source": "yahoo",
            "symbols": sp500_symbols,
            "start": start_date,
            "end": end_date,
            "asset_type": "stock",
        }
    ]

    print("\nDescargando datos históricos desde Yahoo Finance...")
    all_series = manager.fetch_multiple_sources(requests_list)

    print(f"Se han obtenido {len(all_series)} series de precios.\n")
    pretty_preview(all_series, max_points=2)

    # --------------------------------------------------
    # 5. Asignar pesos aleatorios a cada activo y construir la cartera
    # --------------------------------------------------
    print("\nConstruyendo la cartera con pesos aleatorios...")

    raw_weights = [random.random() for _ in all_series]
    total_w = sum(raw_weights)
    norm_weights = [w / total_w for w in raw_weights]

    assets = {}
    for s, w in zip(all_series, norm_weights):
        assets[s.symbol] = {
            "series": s,
            "weight": w,
        }

    portfolio = Portfolio(assets=assets)

    # --------------------------------------------------
    # 6. Generar informe en Markdown
    # --------------------------------------------------
    print("\n\n=== INFORME DE CARTERA (Markdown) ===\n")
    report_md = portfolio.report(horizon_days=30)
    print(report_md)

    # --------------------------------------------------
    # 7. Generar gráfico con la simulación Monte Carlo
    # --------------------------------------------------
    print("\nMostrando gráfico de simulación Monte Carlo de la cartera...")
    portfolio.plots_report(days=30, n_paths=200, show_mean=True)

