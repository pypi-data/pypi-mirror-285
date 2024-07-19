from enum import Enum


class Tarifregionskriterium(str, Enum):
    """
    Mit diesen Kriterien können regionale Bereiche definiert werden.
    """

    NETZ_NUMMER = "NETZ_NUMMER"
    POSTLEITZAHL = "POSTLEITZAHL"
    ORT = "ORT"
    GRUNDVERSORGER_NUMMER = "GRUNDVERSORGER_NUMMER"
    REGION = "REGION"
