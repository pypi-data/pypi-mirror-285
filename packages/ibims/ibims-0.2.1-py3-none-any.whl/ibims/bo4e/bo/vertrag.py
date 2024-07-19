from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..com.unterschrift import Unterschrift
from ..com.vertragskonditionen import Vertragskonditionen
from ..com.vertragsteil import Vertragsteil
from ..enum.sparte import Sparte
from ..enum.typ import Typ
from ..enum.vertragsart import Vertragsart
from ..enum.vertragsstatus import Vertragsstatus
from ..zusatz_attribut import ZusatzAttribut
from .geschaeftspartner import Geschaeftspartner


class Vertrag(BaseModel):
    """
    Modell für die Abbildung von Vertragsbeziehungen;
    Das Objekt dient dazu, alle Arten von Verträgen, die in der Energiewirtschaft Verwendung finden, abzubilden.

    .. raw:: html

        <object data="../_static/images/bo4e/bo/Vertrag.svg" type="image/svg+xml"></object>

    .. HINT::
        `Vertrag JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/bo/Vertrag.json>`_
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
    sparte: Sparte | None = Field(default=None, description="Unterscheidungsmöglichkeiten für die Sparte")
    unterzeichnervp1: list[Unterschrift] | None = Field(
        default=None, description="Unterzeichner des Vertragspartners 1", title="Unterzeichnervp1"
    )
    unterzeichnervp2: list[Unterschrift] | None = Field(
        default=None, description="Unterzeichner des Vertragspartners 2", title="Unterzeichnervp2"
    )
    vertragsart: Vertragsart | None = Field(
        default=None, description="Hier ist festgelegt, um welche Art von Vertrag es sich handelt."
    )
    vertragsbeginn: datetime = Field(
        ..., description="Gibt an, wann der Vertrag beginnt (inklusiv)", title="Vertragsbeginn"
    )
    vertragsende: datetime | None = Field(
        default=None,
        description="Gibt an, wann der Vertrag (voraussichtlich) endet oder beendet wurde (exklusiv)",
        title="Vertragsende",
    )
    vertragskonditionen: Vertragskonditionen | None = Field(
        default=None, description="Festlegungen zu Laufzeiten und Kündigungsfristen"
    )
    vertragsnummer: str = Field(
        ..., description="Eine im Verwendungskontext eindeutige Nummer für den Vertrag", title="Vertragsnummer"
    )
    vertragspartner1: Geschaeftspartner = Field(
        ...,
        description='Der "erstgenannte" Vertragspartner.\nIn der Regel der Aussteller des Vertrags.\nBeispiel: "Vertrag zwischen Vertragspartner 1 ..."',
    )
    vertragspartner2: Geschaeftspartner = Field(..., description='vertragsteile: Optional[list["Vertragsteil"]] = None')
    vertragsstatus: Vertragsstatus | None = Field(default=None, description="Gibt den Status des Vertrags an")
    vertragsteile: list[Vertragsteil] | None = Field(
        default=None, description="Beschreibung zum Vertrag", title="Vertragsteile"
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
