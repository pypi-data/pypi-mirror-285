from enum import Enum


class Titel(str, Enum):
    """
    Übersicht möglicher Titel, z.B. eines Geschäftspartners.
    """

    DR = "DR"
    PROF = "PROF"
    PROF_DR = "PROF_DR"
