from enum import Enum


class Steuerkennzeichen(str, Enum):
    """
    Zur Kennzeichnung verschiedener Steuersätze und Verfahren.
    """

    UST_0 = "UST_0"
    UST_19 = "UST_19"
    UST_16 = "UST_16"
    UST_7 = "UST_7"
    VST_0 = "VST_0"
    VST_19 = "VST_19"
    VST_16 = "VST_16"
    VST_7 = "VST_7"
    RCV = "RCV"
