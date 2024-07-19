from enum import Enum


class Tarifzeit(str, Enum):
    """
    Zur Kennzeichnung verschiedener Tarifzeiten, beispielsweise zur Bepreisung oder zur Verbrauchsermittlung.
    """

    TZ_STANDARD = "TZ_STANDARD"
    TZ_HT = "TZ_HT"
    TZ_NT = "TZ_NT"
