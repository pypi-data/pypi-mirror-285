from enum import Enum


class Vertragsstatus(str, Enum):
    """
    Abbildung einer Statusinformation für Verträge.
    """

    IN_ARBEIT = "IN_ARBEIT"
    UEBERMITTELT = "UEBERMITTELT"
    ANGENOMMEN = "ANGENOMMEN"
    AKTIV = "AKTIV"
    ABGELEHNT = "ABGELEHNT"
    WIDERRUFEN = "WIDERRUFEN"
    STORNIERT = "STORNIERT"
    GEKUENDIGT = "GEKUENDIGT"
    BEENDET = "BEENDET"
