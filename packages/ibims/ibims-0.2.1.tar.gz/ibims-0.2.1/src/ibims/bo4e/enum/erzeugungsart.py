from enum import Enum


class Erzeugungsart(str, Enum):
    """
    Auflistung der Erzeugungsarten von Energie.
    """

    FOSSIL = "FOSSIL"
    KWK = "KWK"
    WIND = "WIND"
    SOLAR = "SOLAR"
    KERNKRAFT = "KERNKRAFT"
    WASSER = "WASSER"
    GEOTHERMIE = "GEOTHERMIE"
    BIOMASSE = "BIOMASSE"
    KOHLE = "KOHLE"
    GAS = "GAS"
    SONSTIGE = "SONSTIGE"
    SONSTIGE_EEG = "SONSTIGE_EEG"
    BIOGAS = "BIOGAS"
    KLIMANEUTRALES_GAS = "KLIMANEUTRALES_GAS"
