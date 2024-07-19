from enum import Enum


class Bemessungsgroesse(str, Enum):
    """
    Zur Abbildung von Messgrössen und zur Verwendung in energiewirtschaftlichen Berechnungen.
    """

    WIRKARBEIT_EL = "WIRKARBEIT_EL"
    LEISTUNG_EL = "LEISTUNG_EL"
    BLINDARBEIT_KAP = "BLINDARBEIT_KAP"
    BLINDARBEIT_IND = "BLINDARBEIT_IND"
    BLINDLEISTUNG_KAP = "BLINDLEISTUNG_KAP"
    BLINDLEISTUNG_IND = "BLINDLEISTUNG_IND"
    WIRKARBEIT_TH = "WIRKARBEIT_TH"
    LEISTUNG_TH = "LEISTUNG_TH"
    VOLUMEN = "VOLUMEN"
    VOLUMENSTROM = "VOLUMENSTROM"
    BENUTZUNGSDAUER = "BENUTZUNGSDAUER"
    ANZAHL = "ANZAHL"
