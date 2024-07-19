from enum import Enum


class Oekozertifikat(str, Enum):
    """
    Zertifikate für Ökostrom von verschiedenen Herausgebern.
    """

    CMS_EE01 = "CMS_EE01"
    CMS_EE02 = "CMS_EE02"
    EECS = "EECS"
    FRAUNHOFER = "FRAUNHOFER"
    BET = "BET"
    KLIMA_INVEST = "KLIMA_INVEST"
    LGA = "LGA"
    FREIBERG = "FREIBERG"
    RECS = "RECS"
    REGS_EGL = "REGS_EGL"
    TUEV = "TUEV"
    TUEV_HESSEN = "TUEV_HESSEN"
    TUEV_NORD = "TUEV_NORD"
    TUEV_RHEINLAND = "TUEV_RHEINLAND"
    TUEV_SUED = "TUEV_SUED"
    TUEV_SUED_EE01 = "TUEV_SUED_EE01"
    TUEV_SUED_EE02 = "TUEV_SUED_EE02"
