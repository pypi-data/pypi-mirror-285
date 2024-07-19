from pydantic import BaseModel, ConfigDict, Field

from ..enum.themengebiet import Themengebiet
from ..zusatz_attribut import ZusatzAttribut


class Zustaendigkeit(BaseModel):
    """
    Enthält die zeitliche Zuordnung eines Ansprechpartners zu Abteilungen und Zuständigkeiten.

    .. raw:: html

        <object data="../_static/images/bo4e/com/Zustaendigkeit.svg" type="image/svg+xml"></object>

    .. HINT::
        `Zustaendigkeit JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Zustaendigkeit.json>`_
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
    abteilung: str | None = Field(
        default=None, description="Berufliche Rolle des Ansprechpartners/ der Person", title="Abteilung"
    )
    position: str | None = Field(
        default=None, description="Berufliche Rolle des Ansprechpartners/ der Person", title="Position"
    )
    themengebiet: Themengebiet | None = Field(
        default=None,
        description="Hier kann eine thematische Zuordnung des Ansprechpartners bzw. der Person angegeben werden",
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
