from enum import Enum


class Marktrolle(str, Enum):
    """
    Diese Rollen kann ein Marktteilnehmer einnehmen.
    """

    BTR = "BTR"
    BIKO = "BIKO"
    BKV = "BKV"
    DP = "DP"
    EIV = "EIV"
    ESA = "ESA"
    KN = "KN"
    LF = "LF"
    MGV = "MGV"
    MSB = "MSB"
    NB = "NB"
    RB = "RB"
    UENB = "UENB"
