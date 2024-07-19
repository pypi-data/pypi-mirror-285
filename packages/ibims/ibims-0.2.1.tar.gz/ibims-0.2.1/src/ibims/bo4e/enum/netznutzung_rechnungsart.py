from enum import Enum


class NetznutzungRechnungsart(str, Enum):
    """
    Abbildung verschiedener in der INVOIC angegebenen Rechnungsarten.
    """

    HANDELSRECHNUNG = "HANDELSRECHNUNG"
    SELBSTAUSGESTELLT = "SELBSTAUSGESTELLT"
