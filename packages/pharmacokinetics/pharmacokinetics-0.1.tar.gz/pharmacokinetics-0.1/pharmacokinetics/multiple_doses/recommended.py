import math
from pharmacokinetics import _handlers

__all__ = [
    "calculateRecommendedInterval",
]

def calculateRecommendedInterval(cmaxDesired, cminDesired, **kwargs) -> float:
    """Calculates the recommended interval between doses.

    :param cmaxDesired: the desired maximum concentration
    :param cminDesired: the desired minimum concentration
    :param **kwargs:
        ke: elimination rate constant
        t12: elimination half-life (alternative to `ke`)
        infusion_duration: duration of infusion (default 0)"""
    ke = _handlers._getPkConstantFromKwargs("ke", "t12", kwargs)
    infusion_duration = kwargs.get("infusion_duration", 0)
    return math.log(cmaxDesired/cminDesired) / ke + infusion_duration
