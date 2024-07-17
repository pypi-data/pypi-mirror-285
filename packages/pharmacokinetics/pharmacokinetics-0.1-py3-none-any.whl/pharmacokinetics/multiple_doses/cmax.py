import math
from pharmacokinetics import _handlers

__all__ = [
    "calculateCmax",
]

def calculateCmax(concentration: float, interval: float, **kwargs) -> float:
    """Calculates the maximum concentration (cmax).

    :param concentration: initial administered concentration
    :param interval: interval between administered doses
    :param **kwargs:
        ke: elimination rate constant
        t12: elimination half-life (alternative to `ke`)"""
    ke = _handlers._getPkConstantFromKwargs("ke", "t12", kwargs)
    return concentration / (1 - math.e**(-ke * interval))
