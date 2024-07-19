from enum import Enum


class Befestigungsart(str, Enum):
    """
    Befestigungsart von Zählern
    """

    STECKTECHNIK = "STECKTECHNIK"
    DREIPUNKT = "DREIPUNKT"
    HUTSCHIENE = "HUTSCHIENE"
    EINSTUTZEN = "EINSTUTZEN"
    ZWEISTUTZEN = "ZWEISTUTZEN"
