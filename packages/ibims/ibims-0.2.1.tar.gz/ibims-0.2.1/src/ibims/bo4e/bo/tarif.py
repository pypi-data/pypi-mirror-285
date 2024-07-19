from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..com.auf_abschlag_regional import AufAbschlagRegional
from ..com.energiemix import Energiemix
from ..com.preisgarantie import Preisgarantie
from ..com.tarifberechnungsparameter import Tarifberechnungsparameter
from ..com.tarifeinschraenkung import Tarifeinschraenkung
from ..com.tarifpreisposition_pro_ort import TarifpreispositionProOrt
from ..com.vertragskonditionen import Vertragskonditionen
from ..com.zeitraum import Zeitraum
from ..enum.kundentyp import Kundentyp
from ..enum.registeranzahl import Registeranzahl
from ..enum.sparte import Sparte
from ..enum.tarifmerkmal import Tarifmerkmal
from ..enum.tariftyp import Tariftyp
from ..enum.typ import Typ
from ..zusatz_attribut import ZusatzAttribut
from .marktteilnehmer import Marktteilnehmer


class Tarif(BaseModel):
    """
    Abbildung eines Tarifs mit regionaler Zuordnung von Preisen und Auf- und Abschlägen

    .. raw:: html

        <object data="../_static/images/bo4e/bo/Tarif.svg" type="image/svg+xml"></object>

    .. HINT::
        `Tarif JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/bo/Tarif.json>`_
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
    typ: Typ = Field(..., alias="_typ", description="Gibt an, wann der Preis zuletzt angepasst wurde")
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
    berechnungsparameter: Tarifberechnungsparameter | None = Field(
        default=None, description="Für die Berechnung der Kosten sind die hier abgebildeten Parameter heranzuziehen"
    )
    bezeichnung: str | None = Field(default=None, description="Name des Tarifs", title="Bezeichnung")
    energiemix: Energiemix | None = Field(default=None, description="Der Energiemix, der für diesen Tarif gilt")
    kundentypen: list[Kundentyp] | None = Field(
        default=None, description="Kundentypen für den der Tarif gilt, z.B. Privatkunden", title="Kundentypen"
    )
    preisgarantie: Preisgarantie | None = Field(default=None, description="Preisgarantie für diesen Tarif")
    preisstand: datetime | None = Field(
        default=None, description="Gibt an, wann der Preis zuletzt angepasst wurde", title="Preisstand"
    )
    registeranzahl: Registeranzahl | None = Field(
        default=None, description="Die Art des Tarifes, z.B. Eintarif oder Mehrtarif"
    )
    sparte: Sparte | None = Field(default=None, description="Strom oder Gas, etc.")
    tarif_auf_abschlaege: list[AufAbschlagRegional] | None = Field(
        default=None,
        alias="tarifAufAbschlaege",
        description="Auf- und Abschläge auf die Preise oder Kosten mit regionaler Eingrenzung",
        title="Tarifaufabschlaege",
    )
    tarifeinschraenkung: Tarifeinschraenkung | None = Field(
        default=None, description="Die Bedingungen und Einschränkungen unter denen ein Tarif angewendet werden kann"
    )
    tarifmerkmale: list[Tarifmerkmal] | None = Field(
        default=None, description="Weitere Merkmale des Tarifs, z.B. Festpreis oder Vorkasse", title="Tarifmerkmale"
    )
    tarifpreise: list[TarifpreispositionProOrt] | None = Field(
        default=None,
        description="Die festgelegten Preise mit regionaler Eingrenzung z.B. für Arbeitspreis, Grundpreis etc.",
        title="Tarifpreise",
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
