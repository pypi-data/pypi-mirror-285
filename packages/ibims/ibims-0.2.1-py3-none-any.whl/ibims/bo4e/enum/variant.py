from enum import Enum


class Variant(str, Enum):
    """
    gridUsageBilling.variant (Netznutzungsabrechnungsvariante)
        Z14: WorkPriceBasicPrice (Arbeitspreis/Grundpreis)
        Z15: WorkPricePerformancePrice (Arbeitspreis/Leistungspreis)
    """

    Z14 = "Z14"
    Z15 = "Z15"
