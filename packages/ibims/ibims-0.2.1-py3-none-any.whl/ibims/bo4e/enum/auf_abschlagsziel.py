from enum import Enum


class AufAbschlagsziel(str, Enum):
    """
    Der Preis, auf den sich ein Auf- oder Abschlag bezieht.
    """

    ARBEITSPREIS_EINTARIF = "ARBEITSPREIS_EINTARIF"
    ARBEITSPREIS_HT = "ARBEITSPREIS_HT"
    ARBEITSPREIS_NT = "ARBEITSPREIS_NT"
    ARBEITSPREIS_HT_NT = "ARBEITSPREIS_HT_NT"
    GRUNDPREIS = "GRUNDPREIS"
    GESAMTPREIS = "GESAMTPREIS"
