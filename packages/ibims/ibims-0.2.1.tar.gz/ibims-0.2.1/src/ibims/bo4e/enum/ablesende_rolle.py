from enum import Enum


class AblesendeRolle(str, Enum):
    """
    Eine (Markt)Rolle, die Verbräuche abliest.
    """

    VNB = "VNB"
    ENDKUNDE = "ENDKUNDE"
    VORIGER_LIEFERANT = "VORIGER_LIEFERANT"
    MSB = "MSB"
    SYSTEM = "SYSTEM"
