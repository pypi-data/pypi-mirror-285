from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..enum.typ import Typ
from ..zusatz_attribut import ZusatzAttribut


class Dokument(BaseModel):
    """
    A generic document reference like for bills, order confirmations and cancellations
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    version: str | None = Field(default="v202401.2.1", alias="_version", title=" Version")
    typ: Typ | None = Field(default=Typ.DOKUMENT, alias="_typ", title=" Typ")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="ZusatzAttribute"
    )
    id: str | None = Field(default=None, alias="_id", title=" Id")
    erstellungsdatum: datetime = Field(..., title="Erstellungsdatum")
    has_been_sent: bool = Field(..., alias="hasBeenSent", title="Hasbeensent")
    dokumentenname: str = Field(..., title="Dokumentenname")
    vorlagenname: str = Field(..., title="Vorlagenname")
