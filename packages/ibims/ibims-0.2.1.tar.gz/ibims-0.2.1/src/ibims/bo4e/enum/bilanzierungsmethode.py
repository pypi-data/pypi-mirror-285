from enum import Enum


class Bilanzierungsmethode(str, Enum):
    """
    Mit dieser Aufzählung kann zwischen den Bilanzierungsmethoden bzw. -grundlagen unterschieden werden.
    """

    RLM = "RLM"
    SLP = "SLP"
    TLP_GEMEINSAM = "TLP_GEMEINSAM"
    TLP_GETRENNT = "TLP_GETRENNT"
    PAUSCHAL = "PAUSCHAL"
