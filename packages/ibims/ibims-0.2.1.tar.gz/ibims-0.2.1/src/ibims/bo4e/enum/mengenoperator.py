from enum import Enum


class Mengenoperator(str, Enum):
    """
    Angabe, wie eine Menge in Bezug auf einen Wert zu bilden ist.
    """

    KLEINER_ALS = "KLEINER_ALS"
    GROESSER_ALS = "GROESSER_ALS"
    GLEICH = "GLEICH"
