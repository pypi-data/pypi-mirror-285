from enum import Enum


class Profiltyp(str, Enum):
    """
    This enum specifies the forecast (Prognosegrundlage)
    """

    SLP_SEP = "SLP_SEP"
    TLP_TEP = "TLP_TEP"
