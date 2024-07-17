import math

__all__ = [
    "halflifeFromDoses",
]

def halflifeFromDoses(dose, remaining, elapsed) -> float:
    """Calculates the half-life based on the dose remaining after a specific time.

    :param dose: the initial dose administered
    :param remaining: the remaining dose at the specified time
    :param elapsed: the time elapsed since the drug has reached peak concentrations"""
    halfLivesPassed = math.log10(remaining/dose) / math.log10(0.5)
    return elapsed / halfLivesPassed
