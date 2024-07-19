from enum import Enum


class ArtikelId(str, Enum):
    """
    Liste von Artikel-IDs, z.B. für standardisierte vom BDEW herausgegebene Artikel,
    die im Strommarkt die BDEW-Artikelnummer ablösen
    """

    FIELD_2_01_7_001 = "2-01-7-001"
    FIELD_2_01_7_002 = "2-01-7-002"
    FIELD_2_01_7_003 = "2-01-7-003"
    FIELD_2_01_7_004 = "2-01-7-004"
    FIELD_2_01_7_005 = "2-01-7-005"
    FIELD_2_01_7_006 = "2-01-7-006"
    FIELD_2_02_0_001 = "2-02-0-001"
    FIELD_2_02_0_002 = "2-02-0-002"
