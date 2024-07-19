from enum import Enum


class AbgabeArt(str, Enum):
    """
    Art der Konzessionsabgabe
    """

    KAS = "KAS"
    SA = "SA"
    SAS = "SAS"
    TA = "TA"
    TAS = "TAS"
    TK = "TK"
    TKS = "TKS"
    TS = "TS"
    TSS = "TSS"
