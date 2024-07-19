from enum import Enum


class Waehrungseinheit(str, Enum):
    """
    In diesem Enum werden die Währungen und ihre Untereinheiten definiert, beispielsweise für die Verwendung in Preisen.
    """

    EUR = "EUR"
    CT = "CT"
