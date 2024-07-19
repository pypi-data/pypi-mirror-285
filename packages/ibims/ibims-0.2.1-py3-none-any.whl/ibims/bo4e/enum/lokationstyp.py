from enum import Enum


class Lokationstyp(str, Enum):
    """
    Gibt an, ob es sich um eine Markt- oder Messlokation handelt.
    """

    MALO = "MALO"
    MELO = "MELO"
