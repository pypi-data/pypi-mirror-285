from pydantic import BaseModel, ConfigDict, Field

from ..enum.invoice_status import InvoiceStatus
from ..enum.sparte import Sparte


class TransaktionsdatenInvoices(BaseModel):
    """
    This class adds additional data to the transaktionsdaten, which is needed for an invoice
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    migration_id: str | None = Field(default=None, title="Migration_id")
    import_fuer_storno_adhoc: str | None = Field(default=None, title="Import_fuer_storno_adhoc")
    sparte: Sparte | None = Field(default=None, title="Sparte")
    pruefidentifikator: str | None = Field(default=None, title="Pruefidentifikator")
    datenaustauschreferenz: str | None = Field(default=None, title="Datenaustauschreferenz")
    nachrichtendatum: str | None = Field(default=None, title="Nachrichtendatum")
    nachrichten_referenznummer: str | None = Field(default=None, title="Nachrichten_referenznummer")
    absender: str | None = Field(default=None, title="Absender")
    empfaenger: str | None = Field(default=None, title="Empfaenger")
    lieferrichtung: str | None = Field(default=None, title="Lieferrichtung")
    referenznummer: str | None = Field(default=None, title="Referenznummer")
    duplikat: str | None = Field(default=None, title="Duplikat")
    status: InvoiceStatus | None = Field(default=InvoiceStatus.ACCEPTED, title="Status")
