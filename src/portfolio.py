# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, List, Optional
import math
import random

import matplotlib.pyplot as plt

from .data_models import PriceSeries
from . import utils_stats


class Portfolio:
    """
    Cartera compuesta por varios activos (PriceSeries) con pesos.
    Ejemplo de `assets` esperado en __init__

    assets = {
        "AAPL": {
              "series": <PriceSeries>,
              "weight": 0.5
    },
    "MSFT": {
        "series": <PriceSeries>,
        "weight": 0.5
    }
  }

  Los pesos se normalizan para que sumen 1.
  """

    def __init__(self, assets: Dict[str, Dict]):
        self.assets = assets
        self._normalize_weights()
        self._ensure_series_stats_ready()

    def _normalize_weights(self):
        total = sum(a["weight"] for a in self.assets.values())
        if total == 0:
            return
        for a in self.assets.values():
            a["weight"] = a["weight"] / total

    def _ensure_series_stats_ready(self):
        """
        Asegura que cada PriceSeries esté limpia y tenga mean_return / stdev_return calculados.
       """
        for a in self.assets.values():
            s: PriceSeries = a["series"]
            s.clean()
            s.update_basic_stats()

    # -------------------------
    # Métricas de la cartera
    # -------------------------
    def expected_daily_return(self) -> Optional[float]:
        """
        μ_port = Σ w_i * μ_i
        """
        total = 0.0
        valid = 0
        for a in self.assets.values():
            w = a["weight"]
            mu_i = a["series"].mean_return
            if mu_i is not None:
                total += w * mu_i
                valid += 1
        return total if valid > 0 else None

    def daily_volatility(self) -> Optional[float]:
        """
        σ_port = sqrt( Σ (w_i * σ_i)^2 )
        Asumimos independencia entre activos (sin covarianzas).
        """
        variance_sum = 0.0
        for a in self.assets.values():
            w = a["weight"]
            sigma_i = a["series"].stdev_return
            if sigma_i is not None:
                variance_sum += (w * sigma_i) ** 2
        if variance_sum <= 0:
            return None
        return math.sqrt(variance_sum)

    def last_portfolio_value(self) -> Optional[float]:
        """
        Valor "base" de la cartera hoy = suma( peso_i * último precio_i ).
        """
        total = 0.0
        valid = 0
        for a in self.assets.values():
            w = a["weight"]
            closes = a["series"]._get_close_prices()
            if closes:
                total += w * closes[-1]
                valid += 1
        return total if valid > 0 else None

    # -------------------------
    # Monte Carlo de la cartera
    # -------------------------
    def monte_carlo(
        self,
        days: int = 30,
        n_paths: int = 1000,
        initial_value: Optional[float] = None,
    ) -> List[List[float]]:
        """
        Simula la evolución futura del VALOR TOTAL de la cartera.
        Asume que el retorno diario de la cartera es Normal(mu_port, sigma_port),
        donde mu_port y sigma_port se calculan a partir de los activos.

        Devuelve lista de trayectorias [ [v0, v1, ..., v_days], ... ].
        """
        mu_port = self.expected_daily_return()
        sigma_port = self.daily_volatility()
        if mu_port is None or sigma_port is None:
            return []

        if initial_value is None:
            initial_value = self.last_portfolio_value()
            if initial_value is None:
                return []

        paths: List[List[float]] = []
        for _ in range(n_paths):
            path = [initial_value]
            for _d in range(days):
                z = random.gauss(0, 1)
                daily_ret = mu_port + sigma_port * z
                next_val = path[-1] * math.exp(daily_ret)
                path.append(next_val)
            paths.append(path)

        return paths

    # -------------------------
    # Reporte en Markdown
    # -------------------------
    def report(self, horizon_days: int = 30) -> str:
        """
        Genera un informe en formato Markdown con:
        - composición de la cartera
        - métricas de riesgo y retorno
        - resumen Monte Carlo
        - advertencias
        """
        mu = self.expected_daily_return()
        sigma = self.daily_volatility()
        v0 = self.last_portfolio_value()

        lines = []
        lines.append("# Informe de Cartera\n")

        lines.append("## Composición (pesos normalizados)")
        for name, a in self.assets.items():
            w_pct = round(a["weight"] * 100, 2)
            lines.append(f"- {name}: {w_pct}%")

        lines.append("\n## Métricas diarias estimadas")
        lines.append(f"- Rentabilidad esperada diaria (media): {mu}")
        lines.append(f"- Volatilidad diaria estimada: {sigma}")
        lines.append(f"- Valor inicial estimado de la cartera: {v0}")

        sims = self.monte_carlo(days=horizon_days, n_paths=500, initial_value=v0)
        if sims:
            finales = [path[-1] for path in sims]
            finales.sort()
            p5 = finales[int(0.05 * len(finales))]
            p50 = finales[int(0.50 * len(finales))]
            p95 = finales[int(0.95 * len(finales))]
            lines.append("\n## Simulación Monte Carlo")
            lines.append(f"- Horizonte simulado: {horizon_days} días")
            lines.append(f"- Escenario pesimista (p5):  {p5}")
            lines.append(f"- Escenario base (p50):     {p50}")
            lines.append(f"- Escenario optimista (p95): {p95}")
        else:
            lines.append("\n## Simulación Monte Carlo")
            lines.append("- No se ha podido simular (faltan datos o stats).")

        # Advertencias
        lines.append("\n## Advertencias")
        for name, a in self.assets.items():
            s = a["series"]
            if s.mean_return is None or s.stdev_return is None:
                lines.append(f"- {name}: datos insuficientes para estadística fiable.")
            if len(s.data) < 5:
                lines.append(f"- {name}: serie extremadamente corta ({len(s.data)} puntos).")
        if abs(sum(a["weight"] for a in self.assets.values()) - 1.0) > 1e-6:
            lines.append("- Los pesos no sumaban 1. Se han normalizado internamente.")

        return "\n".join(lines)

    # -------------------------
    # Visualización
    # -------------------------
    def plots_report(
        self,
        days: int = 30,
        n_paths: int = 200,
        show_mean: bool = True,
    ):
        """
        Grafica varias trayectorias Monte Carlo y (opcionalmente) la media.
        """
        sims = self.monte_carlo(days=days, n_paths=n_paths)
        if not sims:
            print("No se puede graficar: simulación vacía.")
            return

        # Pintamos algunas trayectorias
        for path in sims[:20]:  # para no saturar el gráfico
            plt.plot(path, alpha=0.3)

        if show_mean:
            # media punto a punto
            mean_path = []
            for t in range(len(sims[0])):  # todas tienen el mismo largo
                vals_t = [path[t] for path in sims]
                mean_path.append(sum(vals_t) / len(vals_t))
            plt.plot(mean_path, linewidth=2)

        plt.title("Simulación Monte Carlo de la cartera")
        plt.xlabel("Días simulados")
        plt.ylabel("Valor estimado de la cartera")
        plt.show()
