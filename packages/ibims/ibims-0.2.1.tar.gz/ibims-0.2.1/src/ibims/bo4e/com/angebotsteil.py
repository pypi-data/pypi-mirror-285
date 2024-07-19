from pydantic import BaseModel, ConfigDict, Field

from ..bo.marktlokation import Marktlokation
from ..zusatz_attribut import ZusatzAttribut
from .angebotsposition import Angebotsposition
from .betrag import Betrag
from .menge import Menge
from .zeitraum import Zeitraum


class Angebotsteil(BaseModel):
    """
    Mit dieser Komponente wird ein Teil einer Angebotsvariante abgebildet.
    Hier werden alle Angebotspositionen aggregiert.
    Angebotsteile werden im einfachsten Fall für eine Marktlokation oder Lieferstellenadresse erzeugt.
    Hier werden die Mengen und Gesamtkosten aller Angebotspositionen zusammengefasst.
    Eine Variante besteht mindestens aus einem Angebotsteil.

    .. raw:: html

        <object data="../_static/images/bo4e/com/Angebotsteil.svg" type="image/svg+xml"></object>

    .. HINT::
        `Angebotsteil JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Angebotsteil.json>`_
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    id: str | None = Field(
        default=None,
        alias="_id",
        description='zusatz_attribute: Optional[list["ZusatzAttribut"]] = None\n\n# pylint: disable=duplicate-code\nmodel_config = ConfigDict(\n    alias_generator=camelize,\n    populate_by_name=True,\n    extra="allow",\n    # json_encoders is deprecated, but there is no easy-to-use alternative. The best way would be to create\n    # an annotated version of Decimal, but you would have to use it everywhere in the pydantic models.\n    # See this issue for more info: https://github.com/pydantic/pydantic/issues/6375\n    json_encoders={Decimal: str},\n)',
        title=" Id",
    )
    version: str = Field(
        ..., alias="_version", description='Version der BO-Struktur aka "fachliche Versionierung"', title=" Version"
    )
    anfrage_subreferenz: str | None = Field(
        default=None,
        alias="anfrageSubreferenz",
        description="Identifizierung eines Subkapitels einer Anfrage, beispielsweise das Los einer Ausschreibung",
        title="Anfragesubreferenz",
    )
    gesamtkostenangebotsteil: Betrag | None = Field(
        default=None, description="Summe der Jahresenergiekosten aller in diesem Angebotsteil enthaltenen Lieferstellen"
    )
    gesamtmengeangebotsteil: Menge | None = Field(
        default=None, description="Summe der Verbräuche aller in diesem Angebotsteil eingeschlossenen Lieferstellen"
    )
    lieferstellenangebotsteil: list[Marktlokation] | None = Field(
        default=None,
        description="Summe der Verbräuche aller in diesem Angebotsteil eingeschlossenen Lieferstellen",
        title="Lieferstellenangebotsteil",
    )
    lieferzeitraum: Zeitraum | None = Field(
        default=None,
        description="Hier kann der Belieferungszeitraum angegeben werden, für den dieser Angebotsteil gilt",
    )
    positionen: list[Angebotsposition] | None = Field(
        default=None, description="Einzelne Positionen, die zu diesem Angebotsteil gehören", title="Positionen"
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
