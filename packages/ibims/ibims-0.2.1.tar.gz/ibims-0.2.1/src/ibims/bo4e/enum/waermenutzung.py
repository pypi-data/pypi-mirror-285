from enum import Enum


class Waermenutzung(str, Enum):
    """
    Wärmenutzung Marktlokation
    """

    SPEICHERHEIZUNG = "SPEICHERHEIZUNG"
    WAERMEPUMPE = "WAERMEPUMPE"
    DIREKTHEIZUNG = "DIREKTHEIZUNG"
