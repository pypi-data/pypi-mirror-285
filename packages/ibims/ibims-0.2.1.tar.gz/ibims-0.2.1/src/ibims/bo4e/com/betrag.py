from pydantic import BaseModel, ConfigDict, Field

from ..enum.waehrungscode import Waehrungscode
from ..zusatz_attribut import ZusatzAttribut


class Betrag(BaseModel):
    """
    Die Komponente wird dazu verwendet, Summenbeträge (beispielsweise in Angeboten und Rechnungen) als Geldbeträge
    abzubilden. Die Einheit ist dabei immer die Hauptwährung also Euro, Dollar etc…

    .. raw:: html

        <object data="../_static/images/bo4e/com/Betrag.svg" type="image/svg+xml"></object>

    .. HINT::
        `Betrag JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Betrag.json>`_
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
    waehrung: Waehrungscode | None = Field(default=None, description="Gibt den Betrag des Preises an.")
    wert: float = Field(..., description="Gibt den Betrag des Preises an.", title="Wert")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
