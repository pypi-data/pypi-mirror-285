from enum import Enum


class Zaehlerauspraegung(str, Enum):
    """
    Gibt an, ob es sich um einen Einrichtungs- oder Zweirichtungszähler handelt.
    """

    EINRICHTUNGSZAEHLER = "EINRICHTUNGSZAEHLER"
    ZWEIRICHTUNGSZAEHLER = "ZWEIRICHTUNGSZAEHLER"
