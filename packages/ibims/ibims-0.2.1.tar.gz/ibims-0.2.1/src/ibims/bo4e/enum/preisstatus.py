from enum import Enum


class Preisstatus(str, Enum):
    """
    Statusinformation für Preise
    """

    VORLAEUFIG = "VORLAEUFIG"
    ENDGUELTIG = "ENDGUELTIG"
