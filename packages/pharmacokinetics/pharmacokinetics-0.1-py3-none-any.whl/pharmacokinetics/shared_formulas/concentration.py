import math
from pharmacokinetics import _handlers
from pharmacokinetics import multiple_doses, single_dose

__all__ = [
    "concentrationAtTime",
]

def concentrationAtTime(dose: float, **kwargs) -> float:
    """Calculates the concentration at a specific time (oral administration).

    :param dose: the dosage administered
    :param **kwargs:
        vd: volume of distribution (default 1)
        bioavailability: fraction of drug absorbed into the systemic circulation (default 1)
        ke: elimination rate constant
        t12: elimination half-life (alternative to `ke`)
        ka: absorption rate constant
        t12abs: absorption half-life
        elapsed: time since drug administration
        interval: interval between doses (optional)"""
    ka = _handlers._getPkConstantFromKwargs("ka", "t12abs", kwargs)
    ke = _handlers._getPkConstantFromKwargs("ke", "t12", kwargs)
    bioavailability = kwargs.get("bioavailability", 1)
    elapsed = kwargs.get("elapsed")
    vd = kwargs.get("vd", 1)
    interval = kwargs.get("interval")
    isMultiDose = interval != None

    if isMultiDose:
        fraction = (bioavailability * dose * ka) / (vd * (ka - ke))
        multiplier = math.exp(-ke * elapsed) / (1 - math.exp(-ke * interval))
        multiplier -= math.exp(-ka * elapsed) / (1 - math.exp(-ka * interval))
        return fraction * multiplier
    if ka == ke: # different formula required to prevent undefined value
        k = float(ka)
        fraction = bioavailability * dose * k / vd
        return fraction * elapsed * math.exp(-k * elapsed)
    fraction = (bioavailability * dose * ka) / (vd * (ka - ke))
    multiplier = math.exp(-ke * elapsed) - math.exp(-ka * elapsed)
    return fraction * multiplier
