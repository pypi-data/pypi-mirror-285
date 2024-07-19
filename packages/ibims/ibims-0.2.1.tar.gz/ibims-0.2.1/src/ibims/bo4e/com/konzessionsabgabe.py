from pydantic import BaseModel, ConfigDict, Field

from ..enum.abgabe_art import AbgabeArt
from ..zusatz_attribut import ZusatzAttribut


class Konzessionsabgabe(BaseModel):
    """
    Diese Komponente wird zur Übertagung der Details zu einer Konzessionsabgabe verwendet.

    .. raw:: html

        <object data="../_static/images/bo4e/com/Konzessionsabgabe.svg" type="image/svg+xml"></object>

    .. HINT::
        `Konzessionsabgabe JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Konzessionsabgabe.json>`_
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
    kategorie: str | None = Field(
        default=None, description="Gebührenkategorie der Konzessionsabgabe", title="Kategorie"
    )
    kosten: float | None = Field(default=None, description="Konzessionsabgabe in E/kWh", title="Kosten")
    satz: AbgabeArt | None = Field(default=None, description="Art der Abgabe")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
