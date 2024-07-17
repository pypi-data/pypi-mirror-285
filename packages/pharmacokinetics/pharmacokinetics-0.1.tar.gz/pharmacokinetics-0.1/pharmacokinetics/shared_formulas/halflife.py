import math

__all__ = [
    "calculateConstant",
    "halflifeFromVdCl",
]

def calculateConstant(pkConstant: float) -> float:
    """Returns the half-life or constant (interchangeable).

    :param pkConstant: constant or half-life
    :return: constant or half-life"""
    return math.log(2) / pkConstant

def halflifeFromVdCl(vd: float, cl: float) -> float:
    """Calculates the half-life with volume of distribution and clearance rate.

    :param vd: volume of distribution
    :param cl: clearance rate"""
    return math.log(2) * vd / cl
