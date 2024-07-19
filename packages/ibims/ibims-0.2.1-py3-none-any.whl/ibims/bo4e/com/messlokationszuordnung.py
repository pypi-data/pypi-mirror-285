from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..enum.arithmetische_operation import ArithmetischeOperation
from ..zusatz_attribut import ZusatzAttribut


class Messlokationszuordnung(BaseModel):
    """
    Mit dieser Komponente werden Messlokationen zu Marktlokationen zugeordnet.
    Dabei kann eine arithmetische Operation (Addition, Subtraktion, Multiplikation, Division) angegeben werden,
    mit der die Messlokation zum Verbrauch der Marktlokation beiträgt.

    .. raw:: html

        <object data="../_static/images/bo4e/com/Messlokationszuordnung.svg" type="image/svg+xml"></object>

    .. HINT::
        `Messlokationszuordnung JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Messlokationszuordnung.json>`_
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
    arithmetik: ArithmetischeOperation | None = None
    gueltig_bis: datetime | None = Field(
        default=None, alias="gueltigBis", description="exklusives Endedatum", title="Gueltigbis"
    )
    gueltig_seit: datetime | None = Field(
        default=None,
        alias="gueltigSeit",
        description="gueltig_bis: Optional[pydantic.AwareDatetime] = None",
        title="Gueltigseit",
    )
    messlokations_id: str = Field(
        ...,
        alias="messlokationsId",
        description='arithmetik: Optional["ArithmetischeOperation"] = None\n\ngueltig_seit: Optional[pydantic.AwareDatetime] = None',
        title="Messlokationsid",
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
