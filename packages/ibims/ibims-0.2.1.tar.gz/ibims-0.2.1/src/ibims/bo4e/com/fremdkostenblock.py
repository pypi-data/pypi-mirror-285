from pydantic import BaseModel, ConfigDict, Field

from ..zusatz_attribut import ZusatzAttribut
from .betrag import Betrag
from .fremdkostenposition import Fremdkostenposition


class Fremdkostenblock(BaseModel):
    """
    Komponente zur Abbildung eines Kostenblocks in den Fremdkosten

    .. raw:: html

        <object data="../_static/images/bo4e/com/Fremdkostenblock.svg" type="image/svg+xml"></object>

    .. HINT::
        `Fremdkostenblock JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Fremdkostenblock.json>`_
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
    kostenblockbezeichnung: str | None = Field(
        default=None,
        description="Bezeichnung für einen Kostenblock. Z.B. Netzkosten, Messkosten, Umlagen, etc.",
        title="Kostenblockbezeichnung",
    )
    kostenpositionen: list[Fremdkostenposition] | None = Field(
        default=None,
        description="Hier sind die Details zu einer Kostenposition aufgeführt. Z.B.:\nAlliander Netz Heinsberg GmbH, 2018-02-01, 2019-01-01, Arbeitspreis HT, 3.660 kWh,\n5,8200 ct/kWh, 213,01 €",
        title="Kostenpositionen",
    )
    summe_kostenblock: Betrag | None = Field(
        default=None, alias="summeKostenblock", description="Die Summe aller Kostenpositionen dieses Blocks"
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
