from enum import Enum


class Wertermittlungsverfahren(str, Enum):
    """
    Gibt an, ob es sich um eine Prognose oder eine Messung handelt, beispielsweise bei der Abbildung eines Verbrauchs.
    """

    PROGNOSE = "PROGNOSE"
    MESSUNG = "MESSUNG"
