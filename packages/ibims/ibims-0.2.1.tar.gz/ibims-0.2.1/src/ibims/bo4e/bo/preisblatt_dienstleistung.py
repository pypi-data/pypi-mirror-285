from pydantic import BaseModel, ConfigDict, Field

from ..com.preisposition import Preisposition
from ..com.zeitraum import Zeitraum
from ..enum.bilanzierungsmethode import Bilanzierungsmethode
from ..enum.dienstleistungstyp import Dienstleistungstyp
from ..enum.preisstatus import Preisstatus
from ..enum.sparte import Sparte
from ..enum.typ import Typ
from ..zusatz_attribut import ZusatzAttribut
from .geraet import Geraet
from .marktteilnehmer import Marktteilnehmer


class PreisblattDienstleistung(BaseModel):
    """
    Variante des Preisblattmodells zur Abbildung der Preise für wahlfreie Dienstleistungen

    .. raw:: html

        <object data="../_static/images/bo4e/bo/PreisblattDienstleistung.svg" type="image/svg+xml"></object>

    .. HINT::
        `PreisblattDienstleistung JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/bo/PreisblattDienstleistung.json>`_
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
    typ: Typ = Field(
        ..., alias="_typ", description="Die Preise gelten für Marktlokationen der angebebenen Bilanzierungsmethode"
    )
    version: str = Field(
        ..., alias="_version", description='Version der BO-Struktur aka "fachliche Versionierung"', title=" Version"
    )
    basisdienstleistung: Dienstleistungstyp | None = Field(
        default=None, description="Dienstleistung, für die der Preis abgebildet wird, z.B. Sperrung/Entsperrung"
    )
    bezeichnung: str | None = Field(
        default=None, description="Eine Bezeichnung für das Preisblatt", title="Bezeichnung"
    )
    bilanzierungsmethode: Bilanzierungsmethode | None = Field(
        default=None, description="Die Preise gelten für Marktlokationen der angebebenen Bilanzierungsmethode"
    )
    geraetedetails: Geraet | None = Field(
        default=None,
        description="Hier kann der Preis auf bestimmte Geräte eingegrenzt werden. Z.B. auf die Zählergröße",
    )
    gueltigkeit: Zeitraum | None = Field(default=None, description="Der Zeitraum für den der Preis festgelegt ist")
    herausgeber: Marktteilnehmer | None = Field(
        default=None, description="Der Netzbetreiber, der die Preise veröffentlicht hat"
    )
    inklusive_dienstleistungen: list[Dienstleistungstyp] | None = Field(
        default=None,
        alias="inklusiveDienstleistungen",
        description="Weitere Dienstleistungen, die im Preis enthalten sind",
        title="Inklusivedienstleistungen",
    )
    preispositionen: list[Preisposition] | None = Field(
        default=None,
        description="Die einzelnen Positionen, die mit dem Preisblatt abgerechnet werden können. Z.B. Arbeitspreis, Grundpreis etc",
        title="Preispositionen",
    )
    preisstatus: Preisstatus | None = Field(
        default=None, description="Merkmal, das anzeigt, ob es sich um vorläufige oder endgültige Preise handelt"
    )
    sparte: Sparte | None = Field(default=None, description="Preisblatt gilt für angegebene Sparte")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
