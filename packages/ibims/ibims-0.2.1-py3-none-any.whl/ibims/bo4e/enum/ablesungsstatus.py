from enum import Enum


class Ablesungsstatus(str, Enum):
    """
    State of the reading
    """

    GUELTIG = "GUELTIG"
    UNGUELTIG = "UNGUELTIG"
    ABGERECHNET = "ABGERECHNET"
