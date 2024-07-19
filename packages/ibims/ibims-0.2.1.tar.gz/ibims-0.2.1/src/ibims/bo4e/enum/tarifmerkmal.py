from enum import Enum


class Tarifmerkmal(str, Enum):
    """
    Produktmerkmale im Zusammenhang mit der Tarifdefinition.
    """

    STANDARD = "STANDARD"
    VORKASSE = "VORKASSE"
    PAKET = "PAKET"
    KOMBI = "KOMBI"
    FESTPREIS = "FESTPREIS"
    BAUSTROM = "BAUSTROM"
    HAUSLICHT = "HAUSLICHT"
    HEIZSTROM = "HEIZSTROM"
    ONLINE = "ONLINE"
