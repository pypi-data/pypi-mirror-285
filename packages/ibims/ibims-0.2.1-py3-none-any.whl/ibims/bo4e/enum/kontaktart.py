from enum import Enum


class Kontaktart(str, Enum):
    """
    Gibt an, auf welchem Weg die Person oder der Geschäftspartner kontaktiert werden kann.
    """

    POSTWEG = "POSTWEG"
    TELEFON = "TELEFON"
    FAX = "FAX"
    E_MAIL = "E_MAIL"
    SMS = "SMS"
