from enum import Enum


class Mengeneinheit(str, Enum):
    """
    Einheit: Messgrößen, die per Messung oder Vorgabe ermittelt werden können.
    """

    W = "W"
    WH = "WH"
    KW = "KW"
    KWH = "KWH"
    KVARH = "KVARH"
    MW = "MW"
    MWH = "MWH"
    STUECK = "STUECK"
    KUBIKMETER = "KUBIKMETER"
    SEKUNDE = "SEKUNDE"
    MINUTE = "MINUTE"
    STUNDE = "STUNDE"
    VIERTEL_STUNDE = "VIERTEL_STUNDE"
    TAG = "TAG"
    WOCHE = "WOCHE"
    MONAT = "MONAT"
    QUARTAL = "QUARTAL"
    HALBJAHR = "HALBJAHR"
    JAHR = "JAHR"
    PROZENT = "PROZENT"
    KVAR = "KVAR"
    KWHK = "KWHK"
    VAR = "VAR"
    VARH = "VARH"
