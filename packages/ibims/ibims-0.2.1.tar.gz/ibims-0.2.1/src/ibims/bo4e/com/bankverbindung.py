from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .sepa_info import SepaInfo


class Bankverbindung(BaseModel):
    """
    This component contains bank connection information.
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    id: str | None = Field(default=None, alias="_id", title=" Id")
    iban: str | None = Field(default=None, title="Iban")
    bic: str | None = Field(default=None, title="Bic")
    gueltig_seit: datetime | None = Field(default=None, alias="gueltigSeit", title="Gueltigseit")
    gueltig_bis: datetime | None = Field(default=None, alias="gueltigBis", title="Gueltigbis")
    bankname: str | None = Field(default=None, title="Bankname")
    sepa_info: SepaInfo | None = Field(default=None, alias="sepaInfo")
    kontoinhaber: str | None = Field(default=None, title="Kontoinhaber")
    ouid: int = Field(..., title="Ouid")
