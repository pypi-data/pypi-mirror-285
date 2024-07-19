from enum import Enum


class Vertragsform(str, Enum):
    """
    Aufzählung der Möglichkeiten zu Vertragsformen in Ausschreibungen.
    """

    ONLINE = "ONLINE"
    DIREKT = "DIREKT"
    FAX = "FAX"
