from enum import Enum


class Verbrauchsart(str, Enum):
    """
    Verbrauchsart einer Marktlokation.
    """

    KL = "KL"
    KLW = "KLW"
    KLWS = "KLWS"
    W = "W"
    WS = "WS"
