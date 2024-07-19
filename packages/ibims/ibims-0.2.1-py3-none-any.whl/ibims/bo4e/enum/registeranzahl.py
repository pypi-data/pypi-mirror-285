from enum import Enum


class Registeranzahl(str, Enum):
    """
    Die Registeranzahl wird verwendet zur Charakterisierung von Zählern und daraus resultierenden Tarifen.
    """

    EINTARIF = "EINTARIF"
    ZWEITARIF = "ZWEITARIF"
    MEHRTARIF = "MEHRTARIF"
