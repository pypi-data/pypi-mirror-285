from enum import Enum


class MesstechnischeEinordnung(str, Enum):
    """
    An enum for the messtechnische Einordnung
    """

    IMS = "IMS"
    KME_MME = "KME_MME"
    KEINE_MESSUNG = "KEINE_MESSUNG"
