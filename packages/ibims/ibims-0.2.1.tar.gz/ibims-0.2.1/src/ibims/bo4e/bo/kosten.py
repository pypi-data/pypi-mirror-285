from pydantic import BaseModel, ConfigDict, Field

from ..com.betrag import Betrag
from ..com.kostenblock import Kostenblock
from ..com.zeitraum import Zeitraum
from ..enum.kostenklasse import Kostenklasse
from ..enum.typ import Typ
from ..zusatz_attribut import ZusatzAttribut


class Kosten(BaseModel):
    """
    Dieses BO wird zur Übertagung von hierarchischen Kostenstrukturen verwendet.
    Die Kosten werden dabei in Kostenblöcke und diese wiederum in Kostenpositionen strukturiert.

    .. raw:: html

        <object data="../_static/images/bo4e/bo/Kosten.svg" type="image/svg+xml"></object>

    .. HINT::
        `Kosten JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/bo/Kosten.json>`_
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
    typ: Typ = Field(..., alias="_typ", description="Klasse der Kosten, beispielsweise Fremdkosten")
    version: str = Field(
        ..., alias="_version", description='Version der BO-Struktur aka "fachliche Versionierung"', title=" Version"
    )
    gueltigkeit: Zeitraum | None = Field(default=None, description="Für diesen Zeitraum wurden die Kosten ermittelt")
    kostenbloecke: list[Kostenblock] | None = Field(
        default=None,
        description="In Kostenblöcken werden Kostenpositionen zusammengefasst. Beispiele: Netzkosten, Umlagen, Steuern etc",
        title="Kostenbloecke",
    )
    kostenklasse: Kostenklasse | None = Field(default=None, description="Klasse der Kosten, beispielsweise Fremdkosten")
    summe_kosten: list[Betrag] | None = Field(
        default=None,
        alias="summeKosten",
        description="Die Gesamtsumme über alle Kostenblöcke und -positionen",
        title="Summekosten",
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
