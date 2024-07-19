from enum import Enum


class Messwerterfassung(str, Enum):
    """
    Specify data acquisition method
    """

    FERNAUSLESBAR = "FERNAUSLESBAR"
    MANUELL_AUSGELESENE = "MANUELL_AUSGELESENE"
