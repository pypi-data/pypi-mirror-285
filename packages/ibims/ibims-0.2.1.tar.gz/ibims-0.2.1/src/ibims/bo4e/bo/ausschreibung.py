from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..com.ausschreibungslos import Ausschreibungslos
from ..com.zeitraum import Zeitraum
from ..enum.ausschreibungsportal import Ausschreibungsportal
from ..enum.ausschreibungsstatus import Ausschreibungsstatus
from ..enum.ausschreibungstyp import Ausschreibungstyp
from ..enum.typ import Typ
from ..zusatz_attribut import ZusatzAttribut
from .geschaeftspartner import Geschaeftspartner


class Ausschreibung(BaseModel):
    """
    Das BO Ausschreibung dient zur detaillierten Darstellung von ausgeschriebenen Energiemengen in der Energiewirtschaft

    .. raw:: html

        <object data="../_static/images/bo4e/bo/Ausschreibung.svg" type="image/svg+xml"></object>

    .. HINT::
        `Ausschreibung JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/bo/Ausschreibung.json>`_
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
    typ: Typ = Field(..., alias="_typ", description="Vom Herausgeber der Ausschreibung vergebene eindeutige Nummer")
    version: str = Field(
        ..., alias="_version", description='Version der BO-Struktur aka "fachliche Versionierung"', title=" Version"
    )
    abgabefrist: Zeitraum | None = Field(default=None, description='bindefrist: Optional["Zeitraum"] = None')
    ausschreibender: Geschaeftspartner | None = Field(
        default=None, description='abgabefrist: Optional["Zeitraum"] = None'
    )
    ausschreibungportal: Ausschreibungsportal | None = Field(
        default=None, description="Aufzählung der unterstützten Ausschreibungsportale"
    )
    ausschreibungsnummer: str | None = Field(
        default=None,
        description="Vom Herausgeber der Ausschreibung vergebene eindeutige Nummer",
        title="Ausschreibungsnummer",
    )
    ausschreibungsstatus: Ausschreibungsstatus | None = Field(
        default=None, description="Bezeichnungen für die Ausschreibungsphasen"
    )
    ausschreibungstyp: Ausschreibungstyp | None = Field(
        default=None, description="Aufzählung für die Typisierung von Ausschreibungen"
    )
    bindefrist: Zeitraum | None = Field(
        default=None, description="Die einzelnen Lose, aus denen sich die Ausschreibung zusammensetzt"
    )
    ist_kostenpflichtig: bool | None = Field(
        default=None,
        alias="istKostenpflichtig",
        description="Kennzeichen, ob die Ausschreibung kostenpflichtig ist",
        title="Istkostenpflichtig",
    )
    lose: list[Ausschreibungslos] | None = Field(
        default=None, description="Die einzelnen Lose, aus denen sich die Ausschreibung zusammensetzt", title="Lose"
    )
    veroeffentlichungszeitpunkt: datetime | None = Field(
        default=None,
        description="Gibt den Veröffentlichungszeitpunkt der Ausschreibung an",
        title="Veroeffentlichungszeitpunkt",
    )
    webseite: str | None = Field(
        default=None,
        description="Internetseite, auf der die Ausschreibung veröffentlicht wurde (falls vorhanden)",
        title="Webseite",
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
