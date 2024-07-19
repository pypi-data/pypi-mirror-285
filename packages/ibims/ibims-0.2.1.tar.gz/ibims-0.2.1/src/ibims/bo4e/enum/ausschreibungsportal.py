from enum import Enum


class Ausschreibungsportal(str, Enum):
    """
    Aufzählung der unterstützten Ausschreibungsportale.
    """

    ENPORTAL = "ENPORTAL"
    ENERGIE_AGENTUR = "ENERGIE_AGENTUR"
    BMWI = "BMWI"
    ENERGIE_HANDELSPLATZ = "ENERGIE_HANDELSPLATZ"
    BUND = "BUND"
    VERA_ONLINE = "VERA_ONLINE"
    ISPEX = "ISPEX"
    ENERGIEMARKTPLATZ = "ENERGIEMARKTPLATZ"
    EVERGABE = "EVERGABE"
    DTAD = "DTAD"
