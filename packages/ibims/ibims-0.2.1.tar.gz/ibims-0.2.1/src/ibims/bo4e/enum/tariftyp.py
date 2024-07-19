from enum import Enum


class Tariftyp(str, Enum):
    """
    Zur Differenzierung von Grund/Ersatzversorgungstarifen und sonstigen angebotenen Tarifen.
    """

    GRUND_ERSATZVERSORGUNG = "GRUND_ERSATZVERSORGUNG"
    GRUNDVERSORGUNG = "GRUNDVERSORGUNG"
    ERSATZVERSORGUNG = "ERSATZVERSORGUNG"
    SONDERTARIF = "SONDERTARIF"
