from enum import Enum


class ArithmetischeOperation(str, Enum):
    """
    Mit dieser Aufzählung können arithmetische Operationen festgelegt werden.
    """

    ADDITION = "ADDITION"
    SUBTRAKTION = "SUBTRAKTION"
    MULTIPLIKATION = "MULTIPLIKATION"
    DIVISION = "DIVISION"
