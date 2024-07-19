from pydantic import BaseModel, ConfigDict, Field

from ..com.betrag import Betrag
from ..com.fremdkostenblock import Fremdkostenblock
from ..com.zeitraum import Zeitraum
from ..enum.typ import Typ
from ..zusatz_attribut import ZusatzAttribut


class Fremdkosten(BaseModel):
    """
    Mit diesem BO werden die Fremdkosten, beispielsweise für eine Angebotserstellung oder eine Rechnungsprüfung,
    übertragen.
    Die Fremdkosten enthalten dabei alle Kostenblöcke, die von anderen Marktteilnehmern oder Instanzen erhoben werden.

    .. raw:: html

        <object data="../_static/images/bo4e/bo/Fremdkosten.svg" type="image/svg+xml"></object>

    .. HINT::
        `Fremdkosten JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/bo/Fremdkosten.json>`_
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    id: str | None = Field(
        default=None,
        alias="_id",
        description="Hier können IDs anderer Systeme hinterlegt werden (z.B. eine SAP-GP-Nummer oder eine GUID)",
        title=" Id",
    )
    typ: Typ = Field(..., alias="_typ", description="Für diesen Zeitraum wurden die Kosten ermittelt")
    version: str = Field(
        ..., alias="_version", description='Version der BO-Struktur aka "fachliche Versionierung"', title=" Version"
    )
    gueltigkeit: Zeitraum | None = Field(default=None, description="Für diesen Zeitraum wurden die Kosten ermittelt")
    kostenbloecke: list[Fremdkostenblock] | None = Field(
        default=None,
        description="In Kostenblöcken werden Kostenpositionen zusammengefasst. Beispiele: Netzkosten, Umlagen, Steuern etc",
        title="Kostenbloecke",
    )
    summe_kosten: Betrag | None = Field(
        default=None, alias="summeKosten", description="Die Gesamtsumme über alle Kostenblöcke und -positionen"
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
