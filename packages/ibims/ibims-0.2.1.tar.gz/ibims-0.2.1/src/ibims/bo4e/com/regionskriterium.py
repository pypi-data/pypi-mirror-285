from pydantic import BaseModel, ConfigDict, Field

from ..enum.gueltigkeitstyp import Gueltigkeitstyp
from ..enum.regionskriteriumtyp import Regionskriteriumtyp
from ..zusatz_attribut import ZusatzAttribut


class Regionskriterium(BaseModel):
    """
    Komponente zur Abbildung eines Regionskriteriums

    .. raw:: html

        <object data="../_static/images/bo4e/com/Regionskriterium.svg" type="image/svg+xml"></object>

    .. HINT::
        `Regionskriterium JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Regionskriterium.json>`_
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
    gueltigkeitstyp: Gueltigkeitstyp | None = Field(
        default=None,
        description="Hier wird festgelegt, ob es sich um ein einschließendes oder ausschließendes Kriterium handelt.",
    )
    regionskriteriumtyp: Regionskriteriumtyp | None = Field(
        default=None, description="Hier wird das Kriterium selbst angegeben, z.B. Bundesland."
    )
    wert: str | None = Field(
        default=None,
        description="Der Wert, den das Kriterium annehmen kann, z.B. NRW.\nIm Falle des Regionskriteriumstyp BUNDESWEIT spielt dieser Wert keine Rolle.",
        title="Wert",
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
