from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..zusatz_attribut import ZusatzAttribut


class Unterschrift(BaseModel):
    """
    Modellierung einer Unterschrift, z.B. für Verträge, Angebote etc.

    .. raw:: html

        <object data="../_static/images/bo4e/com/Unterschrift.svg" type="image/svg+xml"></object>

    .. HINT::
        `Unterschrift JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Unterschrift.json>`_
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
    datum: datetime | None = Field(
        default=None, description="Ort, an dem die Unterschrift geleistet wird", title="Datum"
    )
    name: str | None = Field(default=None, description="Name des Unterschreibers", title="Name")
    ort: str | None = Field(default=None, description="Ort, an dem die Unterschrift geleistet wird", title="Ort")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
