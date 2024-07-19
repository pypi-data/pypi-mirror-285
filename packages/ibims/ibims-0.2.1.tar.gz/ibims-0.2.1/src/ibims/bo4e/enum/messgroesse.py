from enum import Enum


class Messgroesse(str, Enum):
    """
    Gibt die physikalische Größe an, die gemessen wurde.
    """

    STROM = "STROM"
    SPANNUNG = "SPANNUNG"
    WIRKLEISTUNG = "WIRKLEISTUNG"
    BLINDLEISTUNG = "BLINDLEISTUNG"
    DRUCK = "DRUCK"
    LASTGANG = "LASTGANG"
    LASTPROFIL = "LASTPROFIL"
    TEMPERATUR = "TEMPERATUR"
    ZZAHL = "ZZAHL"
    BRENNWERT = "BRENNWERT"
    GRADTZAGSZAHLEN = "GRADTZAGSZAHLEN"
    VOLUMENSTROM = "VOLUMENSTROM"
    PREISE = "PREISE"
