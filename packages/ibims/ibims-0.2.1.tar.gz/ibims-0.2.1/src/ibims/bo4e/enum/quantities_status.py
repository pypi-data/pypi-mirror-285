from enum import Enum


class QuantitiesStatus(str, Enum):
    """
    QuantitiesStatus describes the possible states of a quantity
    """

    CANCELLED = "CANCELLED"
    DECISION = "DECISION"
    IGNORED = "IGNORED"
    OBJECTED = "OBJECTED"
    RECEIVED = "RECEIVED"
    VALID = "VALID"
