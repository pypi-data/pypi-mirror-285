from pydantic import BaseModel, ConfigDict, Field

from ..zusatz_attribut import ZusatzAttribut
from .betrag import Betrag
from .menge import Menge
from .preis import Preis


class Angebotsposition(BaseModel):
    """
    Unterhalb von Angebotsteilen sind die Angebotspositionen eingebunden.
    Hier werden die angebotenen Bestandteile einzeln aufgeführt. Beispiel:
    Positionsmenge: 4000 kWh
    Positionspreis: 24,56 ct/kWh
    Positionskosten: 982,40 EUR

    .. raw:: html

        <object data="../_static/images/bo4e/com/Angebotsposition.svg" type="image/svg+xml"></object>

    .. HINT::
        `Angebotsposition JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Angebotsposition.json>`_
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
    positionsbezeichnung: str | None = Field(
        default=None, description="Bezeichnung der jeweiligen Position des Angebotsteils", title="Positionsbezeichnung"
    )
    positionskosten: Betrag | None = Field(
        default=None, description="Kosten (positionspreis * positionsmenge) für diese Angebotsposition"
    )
    positionsmenge: Menge | None = Field(
        default=None, description="Menge des angebotenen Artikels (z.B. Wirkarbeit in kWh), in dieser Angebotsposition"
    )
    positionspreis: Preis | None = Field(
        default=None, description="Preis pro Einheit/Stückpreis des angebotenen Artikels."
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
