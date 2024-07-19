from pydantic import BaseModel, ConfigDict, Field

from ..enum.marktrolle import Marktrolle
from ..enum.verwendungszweck import Verwendungszweck
from ..zusatz_attribut import ZusatzAttribut


class VerwendungszweckProMarktrolle(BaseModel):
    """
    Dient zur Identifizierung des Verwendungszwecks der Marktrolle an der Marktlokation, der die Werte zu übermitteln sind.

    .. raw:: html

        <object data="../_static/images/bo4e/com/Verwendungszweck.svg" type="image/svg+xml"></object>

    .. HINT::
        `Verwendungszweck JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Verwendungszweck.json>`_
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
    marktrolle: Marktrolle | None = Field(default=None, description='Zwecke: Optional[list["Verwendungszweck"]] = None')
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
    zwecke: list[Verwendungszweck] | None = Field(default=None, description="Verwendungszwecke", title="Zwecke")
