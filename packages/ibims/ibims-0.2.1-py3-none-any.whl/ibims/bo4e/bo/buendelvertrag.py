from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..com.unterschrift import Unterschrift
from ..com.vertragskonditionen import Vertragskonditionen
from ..enum.sparte import Sparte
from ..enum.typ import Typ
from ..enum.vertragsart import Vertragsart
from ..enum.vertragsstatus import Vertragsstatus
from ..zusatz_attribut import ZusatzAttribut
from .geschaeftspartner import Geschaeftspartner
from .vertrag import Vertrag


class Buendelvertrag(BaseModel):
    """
    Abbildung eines Bündelvertrags.
    Es handelt sich hierbei um eine Liste von Einzelverträgen, die in einem Vertragsobjekt gebündelt sind.

    .. raw:: html

        <object data="../_static/images/bo4e/bo/Buendelvertrag.svg" type="image/svg+xml"></object>

    .. HINT::
        `Buendelvertrag JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/bo/Buendelvertrag.json>`_
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
    typ: Typ = Field(..., alias="_typ", description="Der Typ des Geschäftsobjektes")
    version: str = Field(
        ..., alias="_version", description='Version der BO-Struktur aka "fachliche Versionierung"', title=" Version"
    )
    beschreibung: str | None = Field(default=None, description="Beschreibung zum Vertrag", title="Beschreibung")
    einzelvertraege: list[Vertrag] | None = Field(
        default=None, description="Die Liste mit den Einzelverträgen zu den Abnahmestellen", title="Einzelvertraege"
    )
    sparte: Sparte | None = Field(default=None, description="Unterscheidungsmöglichkeiten für die Sparte")
    unterzeichnervp1: list[Unterschrift] | None = Field(
        default=None, description="Unterzeichner des Vertragspartners1", title="Unterzeichnervp1"
    )
    unterzeichnervp2: list[Unterschrift] | None = Field(
        default=None, description="Unterzeichner des Vertragspartners2", title="Unterzeichnervp2"
    )
    vertragsart: Vertragsart | None = Field(
        default=None,
        description="Hier ist festgelegt, um welche Art von Vertrag es sich handelt. Z.B. Netznutzungvertrag",
    )
    vertragsbeginn: datetime | None = Field(
        default=None, description="Gibt an, wann der Vertrag beginnt (inklusiv)", title="Vertragsbeginn"
    )
    vertragsende: datetime | None = Field(
        default=None,
        description="Gibt an, wann der Vertrag (voraussichtlich) endet oder beendet wurde (exklusiv)",
        title="Vertragsende",
    )
    vertragskonditionen: list[Vertragskonditionen] | None = Field(
        default=None, description="Festlegungen zu Laufzeiten und Kündigungsfristen", title="Vertragskonditionen"
    )
    vertragsnummer: str | None = Field(
        default=None, description="Eine im Verwendungskontext eindeutige Nummer für den Vertrag", title="Vertragsnummer"
    )
    vertragspartner1: Geschaeftspartner | None = Field(
        default=None, description='Beispiel: "Vertrag zwischen Vertagspartner 1 ..."'
    )
    vertragspartner2: Geschaeftspartner | None = Field(
        default=None, description='Beispiel "Vertrag zwischen Vertagspartner 1 und Vertragspartner 2"'
    )
    vertragsstatus: Vertragsstatus | None = Field(default=None, description="Gibt den Status des Vertrages an")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
