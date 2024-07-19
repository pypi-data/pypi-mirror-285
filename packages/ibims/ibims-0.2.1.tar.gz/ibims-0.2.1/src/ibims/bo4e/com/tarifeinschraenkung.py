from pydantic import BaseModel, ConfigDict, Field

from ..bo.geraet import Geraet
from ..enum.voraussetzungen import Voraussetzungen
from ..zusatz_attribut import ZusatzAttribut
from .menge import Menge


class Tarifeinschraenkung(BaseModel):
    """
    Mit dieser Komponente werden Einschränkungen für die Anwendung von Tarifen modelliert.

    .. raw:: html

        <object data="../_static/images/bo4e/com/Tarifeinschraenkung.svg" type="image/svg+xml"></object>

    .. HINT::
        `Tarifeinschraenkung JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Tarifeinschraenkung.json>`_
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
    einschraenkungleistung: list[Menge] | None = Field(
        default=None,
        description="Die vereinbarte Leistung, die (näherungsweise) abgenommen wird.\nInsbesondere Gastarife können daran gebunden sein, dass die Leistung einer vereinbarten Höhe entspricht.",
        title="Einschraenkungleistung",
    )
    einschraenkungzaehler: list[Geraet] | None = Field(
        default=None,
        description="Liste der Zähler/Geräte, die erforderlich sind, damit dieser Tarif zur Anwendung gelangen kann.\n(Falls keine Zähler angegeben sind, ist der Tarif nicht an das Vorhandensein bestimmter Zähler gebunden.)",
        title="Einschraenkungzaehler",
    )
    voraussetzungen: list[Voraussetzungen] | None = Field(
        default=None,
        description="Voraussetzungen, die erfüllt sein müssen, damit dieser Tarif zur Anwendung kommen kann",
        title="Voraussetzungen",
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
    zusatzprodukte: list[str] | None = Field(
        default=None,
        description="Weitere Produkte, die gemeinsam mit diesem Tarif bestellt werden können",
        title="Zusatzprodukte",
    )
