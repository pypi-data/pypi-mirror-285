from enum import Enum


class Messart(str, Enum):
    """
    Gibt an, auf welche Art gemessen wurde.
    """

    AKTUELLERWERT = "AKTUELLERWERT"
    MITTELWERT = "MITTELWERT"
    MAXIMALWERT = "MAXIMALWERT"
