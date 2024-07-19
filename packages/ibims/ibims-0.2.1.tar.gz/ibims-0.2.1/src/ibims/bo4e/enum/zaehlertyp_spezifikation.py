from enum import Enum


class ZaehlertypSpezifikation(str, Enum):
    """
    Bei diesem Enum handelt es sich um die Abbildung von besonderen Zählertyp-Spezifikationen der Sparten Strom und Gas.
    """

    EDL40 = "EDL40"
    EDL21 = "EDL21"
    SONSTIGER_EHZ = "SONSTIGER_EHZ"
    MME_STANDARD = "MME_STANDARD"
    MME_MEDA = "MME_MEDA"
