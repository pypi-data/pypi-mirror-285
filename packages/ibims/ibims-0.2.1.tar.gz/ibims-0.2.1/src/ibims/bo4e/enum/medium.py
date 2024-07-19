from enum import Enum


class Medium(str, Enum):
    """
    Gibt ein physikalisches Medium an.
    """

    STROM = "STROM"
    GAS = "GAS"
    WASSER = "WASSER"
    DAMPF = "DAMPF"
