import math

__all__ = [
    "_getPkConstantFromKwargs",
]

def _getPkConstantFromKwargs(constValueName: str, t12ValueName: str, kwargs: dict):
    """Returns the value of `constValueName` if it exists within the `kwargs` dictionary, otherwise it returns `t12ValueName`."""
    return kwargs.get(constValueName) if kwargs.get(constValueName) != None else math.log(2) / kwargs.get(t12ValueName)
