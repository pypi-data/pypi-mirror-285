from enum import Enum


class Ausschreibungstyp(str, Enum):
    """
    Aufzählung für die Typisierung von Ausschreibungen.
    """

    PRIVATRECHTLICH = "PRIVATRECHTLICH"
    OEFFENTLICHRECHTLICH = "OEFFENTLICHRECHTLICH"
    EUROPAWEIT = "EUROPAWEIT"
