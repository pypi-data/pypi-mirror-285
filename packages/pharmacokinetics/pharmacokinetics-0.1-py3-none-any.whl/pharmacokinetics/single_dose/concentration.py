import math
from pharmacokinetics import _handlers

__all__ = [
    "calculateConcentration",
    "calculateRemaining",
]

def calculateConcentration(dose: float, vd: float, bioavailability: float = 1) -> float:
    """Calculates the concentration of a substance.

    :param dose: the dosage of the substance administered
    :param vd: volume of distribution
    :param bioavailability: fraction of the drug absorbed into the systemic circulation (default 1)"""
    return (dose * bioavailability) / vd

def calculateRemaining(concentration: float, elapsed: float, **kwargs) -> float:
    """Calculates the concentration remaining after a specified time.

    :param concentration: the initial concentration
    :param elapsed: time passed since peak concentrations were reached
    :param **kwargs:
        ke: elimination rate constant
        t12: elimination half-life (alternative to `ke`)"""
    ke = _handlers._getPkConstantFromKwargs("ke", "t12", kwargs)
    return concentration * math.e**(-ke * elapsed)
