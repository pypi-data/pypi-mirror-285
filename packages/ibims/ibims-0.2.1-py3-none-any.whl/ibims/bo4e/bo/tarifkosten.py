from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..com.energiemix import Energiemix
from ..com.vertragskonditionen import Vertragskonditionen
from ..com.zeitraum import Zeitraum
from ..enum.kundentyp import Kundentyp
from ..enum.registeranzahl import Registeranzahl
from ..enum.sparte import Sparte
from ..enum.tarifmerkmal import Tarifmerkmal
from ..enum.tariftyp import Tariftyp
from ..enum.typ import Typ
from ..zusatz_attribut import ZusatzAttribut
from .kosten import Kosten
from .marktteilnehmer import Marktteilnehmer


class Tarifkosten(BaseModel):
    """
    Objekt zur Kommunikation von Kosten, die im Rahmen der Tarifanwendung entstehen

    .. raw:: html

        <object data="../_static/images/bo4e/bo/Tarifkosten.svg" type="image/svg+xml"></object>

    .. HINT::
        `Tarifkosten JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/bo/Tarifkosten.json>`_
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
    typ: Typ = Field(..., alias="_typ", description="Name des Tarifs")
    version: str = Field(
        ..., alias="_version", description='Version der BO-Struktur aka "fachliche Versionierung"', title=" Version"
    )
    anbieter: Marktteilnehmer | None = Field(
        default=None, description="Der Marktteilnehmer (Lieferant), der diesen Tarif anbietet"
    )
    anbietername: str | None = Field(
        default=None, description="Der Name des Marktpartners, der den Tarif anbietet", title="Anbietername"
    )
    anwendung_von: datetime | None = Field(
        default=None,
        alias="anwendungVon",
        description='Angabe des inklusiven Zeitpunkts, ab dem der Tarif bzw. der Preis angewendet und abgerechnet wird,\nz.B. "2021-07-20T18:31:48Z"',
        title="Anwendungvon",
    )
    bemerkung: str | None = Field(default=None, description="Freitext", title="Bemerkung")
    bezeichnung: str | None = Field(default=None, description="Name des Tarifs", title="Bezeichnung")
    energiemix: Energiemix | None = Field(default=None, description="Der Energiemix, der für diesen Tarif gilt")
    kosten: Kosten | None = Field(
        default=None,
        description="Referenz (Link) zu einem Kostenobjekt, in dem die Kosten für die Anwendung\ndes Tarifs auf eine Abnahmesituation berechnet wurden",
    )
    kundentypen: list[Kundentyp] | None = Field(
        default=None, description="Kundentypen für den der Tarif gilt, z.B. Privatkunden", title="Kundentypen"
    )
    registeranzahl: Registeranzahl | None = Field(
        default=None, description="Die Art des Tarifes, z.B. Eintarif oder Mehrtarif"
    )
    sparte: Sparte | None = Field(default=None, description="Strom oder Gas, etc.")
    tarifmerkmale: list[Tarifmerkmal] | None = Field(
        default=None, description="Weitere Merkmale des Tarifs, z.B. Festpreis oder Vorkasse", title="Tarifmerkmale"
    )
    tariftyp: Tariftyp | None = Field(
        default=None, description="Hinweis auf den Tariftyp, z.B. Grundversorgung oder Sondertarif"
    )
    vertragskonditionen: Vertragskonditionen | None = Field(
        default=None, description="Mindestlaufzeiten und Kündigungsfristen zusammengefasst"
    )
    website: str | None = Field(
        default=None, description="Internetseite auf dem der Tarif zu finden ist", title="Website"
    )
    zeitliche_gueltigkeit: Zeitraum | None = Field(
        default=None, alias="zeitlicheGueltigkeit", description="Angabe, in welchem Zeitraum der Tarif gültig ist"
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
