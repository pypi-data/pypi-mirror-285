from enum import Enum


class Angebotsstatus(str, Enum):
    """
    Gibt den Status eines Angebotes an.
    """

    KONZEPTION = "KONZEPTION"
    UNVERBINDLICH = "UNVERBINDLICH"
    VERBINDLICH = "VERBINDLICH"
    BEAUFTRAGT = "BEAUFTRAGT"
    UNGUELTIG = "UNGUELTIG"
    ABGELEHNT = "ABGELEHNT"
    NACHGEFASST = "NACHGEFASST"
    AUSSTEHEND = "AUSSTEHEND"
    ERLEDIGT = "ERLEDIGT"
