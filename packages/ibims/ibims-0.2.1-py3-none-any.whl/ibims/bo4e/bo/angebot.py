from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..com.angebotsvariante import Angebotsvariante
from ..enum.sparte import Sparte
from ..enum.typ import Typ
from ..zusatz_attribut import ZusatzAttribut
from .geschaeftspartner import Geschaeftspartner
from .person import Person


class Angebot(BaseModel):
    """
    Mit diesem BO kann ein Versorgungsangebot zur Strom- oder Gasversorgung oder die Teilnahme an einer Ausschreibung
    übertragen werden. Es können verschiedene Varianten enthalten sein (z.B. ein- und mehrjährige Laufzeit).
    Innerhalb jeder Variante können Teile enthalten sein, die jeweils für eine oder mehrere Marktlokationen erstellt
    werden.

    .. raw:: html

        <object data="../_static/images/bo4e/bo/Angebot.svg" type="image/svg+xml"></object>

    .. HINT::
        `Angebot JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/bo/Angebot.json>`_
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
    typ: Typ = Field(..., alias="_typ", description="Eindeutige Nummer des Angebotes")
    version: str = Field(
        ..., alias="_version", description='Version der BO-Struktur aka "fachliche Versionierung"', title=" Version"
    )
    anfragereferenz: str | None = Field(
        default=None,
        description="Bis zu diesem Zeitpunkt (Tag/Uhrzeit) inklusive gilt das Angebot",
        title="Anfragereferenz",
    )
    angebotsdatum: datetime | None = Field(
        default=None, description="Erstellungsdatum des Angebots", title="Angebotsdatum"
    )
    angebotsgeber: Geschaeftspartner | None = Field(default=None, description="Ersteller des Angebots")
    angebotsnehmer: Geschaeftspartner | None = Field(default=None, description="Empfänger des Angebots")
    angebotsnummer: str | None = Field(
        default=None, description="Eindeutige Nummer des Angebotes", title="Angebotsnummer"
    )
    bindefrist: datetime | None = Field(
        default=None, description="Bis zu diesem Zeitpunkt (Tag/Uhrzeit) inklusive gilt das Angebot", title="Bindefrist"
    )
    sparte: Sparte | None = Field(default=None, description="Sparte, für die das Angebot abgegeben wird (Strom/Gas)")
    unterzeichner_angebotsgeber: Person | None = Field(
        default=None,
        alias="unterzeichnerAngebotsgeber",
        description="Person, die als Angebotsgeber das Angebots ausgestellt hat",
    )
    unterzeichner_angebotsnehmer: Person | None = Field(
        default=None,
        alias="unterzeichnerAngebotsnehmer",
        description="Person, die als Angebotsnehmer das Angebot angenommen hat",
    )
    varianten: list[Angebotsvariante] | None = Field(
        default=None,
        description="Eine oder mehrere Varianten des Angebots mit den Angebotsteilen;\nEin Angebot besteht mindestens aus einer Variante.",
        title="Varianten",
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
