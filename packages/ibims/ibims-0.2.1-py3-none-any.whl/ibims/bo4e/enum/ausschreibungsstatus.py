from enum import Enum


class Ausschreibungsstatus(str, Enum):
    """
    Bezeichnungen für die Ausschreibungsphasen
    """

    PHASE1 = "PHASE1"
    PHASE2 = "PHASE2"
    PHASE3 = "PHASE3"
    PHASE4 = "PHASE4"
