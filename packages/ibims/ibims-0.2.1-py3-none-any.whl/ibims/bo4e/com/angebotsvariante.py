from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..enum.angebotsstatus import Angebotsstatus
from ..zusatz_attribut import ZusatzAttribut
from .angebotsteil import Angebotsteil
from .betrag import Betrag
from .menge import Menge


class Angebotsvariante(BaseModel):
    """
    Führt die verschiedenen Ausprägungen der Angebotsberechnung auf

    .. raw:: html

        <object data="../_static/images/bo4e/com/Angebotsvariante.svg" type="image/svg+xml"></object>

    .. HINT::
        `Angebotsvariante JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Angebotsvariante.json>`_
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
    angebotsstatus: Angebotsstatus | None = Field(default=None, description="Gibt den Status eines Angebotes an.")
    bindefrist: datetime | None = Field(
        default=None, description="Bis zu diesem Zeitpunkt gilt die Angebotsvariante", title="Bindefrist"
    )
    erstellungsdatum: datetime | None = Field(
        default=None, description="Datum der Erstellung der Angebotsvariante", title="Erstellungsdatum"
    )
    gesamtkosten: Betrag | None = Field(default=None, description="Aufsummierte Kosten aller Angebotsteile")
    gesamtmenge: Menge | None = Field(default=None, description="Aufsummierte Wirkarbeitsmenge aller Angebotsteile")
    teile: list[Angebotsteil] | None = Field(
        default=None, description="Aufsummierte Wirkarbeitsmenge aller Angebotsteile", title="Teile"
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
