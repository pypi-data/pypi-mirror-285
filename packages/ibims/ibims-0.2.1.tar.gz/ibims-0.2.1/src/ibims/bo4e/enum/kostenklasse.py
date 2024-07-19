from enum import Enum


class Kostenklasse(str, Enum):
    """
    Kostenklassen bilden die oberste Ebene der verschiedenen Kosten.
    In der Regel werden die Gesamtkosten einer Kostenklasse in einer App berechnet.
    """

    FREMDKOSTEN = "FREMDKOSTEN"
    BESCHAFFUNG = "BESCHAFFUNG"
    SELBSTKOSTEN = "SELBSTKOSTEN"
    MARGEN = "MARGEN"
    ENERGIEVERSORGUNGSKOSTEN = "ENERGIEVERSORGUNGSKOSTEN"
