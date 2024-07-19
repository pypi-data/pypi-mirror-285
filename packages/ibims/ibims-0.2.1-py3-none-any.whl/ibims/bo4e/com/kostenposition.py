from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..zusatz_attribut import ZusatzAttribut
from .betrag import Betrag
from .menge import Menge
from .preis import Preis


class Kostenposition(BaseModel):
    """
    Diese Komponente wird zur Übertagung der Details zu einer Kostenposition verwendet.

    .. raw:: html

        <object data="../_static/images/bo4e/com/Kostenposition.svg" type="image/svg+xml"></object>

    .. HINT::
        `Kostenposition JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Kostenposition.json>`_
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
    artikelbezeichnung: str | None = Field(
        default=None,
        description="Bezeichnung für den Artikel für den die Kosten ermittelt wurden. Beispiel: Arbeitspreis HT",
        title="Artikelbezeichnung",
    )
    artikeldetail: str | None = Field(
        default=None,
        description="Detaillierung des Artikels (optional). Beispiel: 'Drehstromzähler'",
        title="Artikeldetail",
    )
    betrag_kostenposition: Betrag | None = Field(
        default=None,
        alias="betragKostenposition",
        description="Der errechnete Gesamtbetrag der Position als Ergebnis der Berechnung <Menge * Einzelpreis> oder\n<Einzelpreis / (Anzahl Tage Jahr) * zeitmenge>",
    )
    bis: datetime | None = Field(
        default=None, description="exklusiver bis-Zeitpunkt der Kostenzeitscheibe", title="Bis"
    )
    einzelpreis: Preis | None = Field(
        default=None, description="Der Preis für eine Einheit. Beispiele: 5,8200 ct/kWh oder 55 €/Jahr."
    )
    menge: Menge | None = Field(
        default=None, description="Die Menge, die in die Kostenberechnung eingeflossen ist. Beispiel: 3.660 kWh"
    )
    positionstitel: str | None = Field(
        default=None,
        description="Ein Titel für die Zeile. Hier kann z.B. der Netzbetreiber eingetragen werden, wenn es sich um Netzkosten handelt.",
        title="Positionstitel",
    )
    von: datetime | None = Field(
        default=None, description="inklusiver von-Zeitpunkt der Kostenzeitscheibe", title="Von"
    )
    zeitmenge: Menge | None = Field(
        default=None, description="Detaillierung des Artikels (optional). Beispiel: 'Drehstromzähler'"
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
