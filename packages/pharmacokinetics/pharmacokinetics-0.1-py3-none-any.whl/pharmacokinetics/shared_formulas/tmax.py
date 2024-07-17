import math
from pharmacokinetics import _handlers

__all__ = [
    "calculateTmax",
]

def calculateTmax(**kwargs) -> float:
    """Calculates the time to reach maximum concentration (tmax).

    :param **kwargs:
        interval: the interval between dose administration (optional)
        ka: absorption rate constant
        t12abs: absorption half-life (alternative to `ka`)
        ke: elimination rate constant
        t12: elimination half-life (alternative to `ke`)"""
    ka = _handlers._getPkConstantFromKwargs("ka", "t12abs", kwargs)
    ke = _handlers._getPkConstantFromKwargs("ke", "t12", kwargs)
    interval = kwargs.get("interval")
    isMultipleDoses = interval != None

    if isMultipleDoses:
        numeratorComponents = []
        numeratorComponents.append(ka * (1 - math.exp(-ke * interval)))
        numeratorComponents.append(ke * (1 - math.exp(-ka * interval)))
        numerator = math.log(numeratorComponents[0] / numeratorComponents[1])
        return numerator / (ka - ke)
    if ka == ke:
        return 1 / ka
    return 1 / (ka - ke) * math.log(ka / ke)
