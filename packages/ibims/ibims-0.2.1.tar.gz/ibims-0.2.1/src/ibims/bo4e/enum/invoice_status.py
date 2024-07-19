from enum import Enum


class InvoiceStatus(str, Enum):
    """
    InvoiceStatus describes the possible states of an invoice
    """

    RECEIVED = "received"
    IGNORED = "ignored"
    DECLINED = "declined"
    CANCELLED = "cancelled"
    ACCEPTED = "accepted"
    MANUAL_DECISION = "manual_decision"
