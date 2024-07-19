from enum import Enum


class Preismodell(str, Enum):
    """
    Bezeichnung der Preismodelle in Ausschreibungen für die Energielieferung.
    """

    FESTPREIS = "FESTPREIS"
    TRANCHE = "TRANCHE"
