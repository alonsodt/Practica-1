import math
from typing import List, Optional


def log_returns(prices: List[float]) -> List[float]:
    """
    Calcula rendimientos logarítmicos: ln(p_t / p_{t-1})
    Ignora saltos donde no haya ambos precios.
    """
    rets = []
    for i in range(1, len(prices)):
        p_prev = prices[i - 1]
        p_curr = prices[i]
        if p_prev is not None and p_curr is not None and p_prev > 0:
            r = math.log(p_curr / p_prev)
            rets.append(r)
    return rets


def mean(xs: List[float]) -> Optional[float]:
    if not xs:
        return None
    return sum(xs) / len(xs)


def stdev(xs: List[float]) -> Optional[float]:
    """
    Desviación típica muestral.
    """
    n = len(xs)
    if n < 2:
        return 0.0
    mu = mean(xs)
    var = sum((x - mu) ** 2 for x in xs) / (n - 1)
    return math.sqrt(var)
