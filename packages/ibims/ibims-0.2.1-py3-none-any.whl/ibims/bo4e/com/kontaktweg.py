from pydantic import BaseModel, ConfigDict, Field

from ..enum.kontaktart import Kontaktart
from ..zusatz_attribut import ZusatzAttribut


class Kontaktweg(BaseModel):
    """
    Die Komponente wird dazu verwendet, die Kontaktwege innerhalb des BOs Person darzustellen

    .. raw:: html

        <object data="../_static/images/bo4e/com/Kontakt.svg" type="image/svg+xml"></object>

    .. HINT::
        `Kontakt JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Kontakt.json>`_
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
    beschreibung: str | None = Field(
        default=None, description='Spezifikation, beispielsweise "Durchwahl", "Sammelnummer" etc.', title="Beschreibung"
    )
    ist_bevorzugter_kontaktweg: bool | None = Field(
        default=None,
        alias="istBevorzugterKontaktweg",
        description="Gibt an, ob es sich um den bevorzugten Kontaktweg handelt.",
        title="Istbevorzugterkontaktweg",
    )
    kontaktart: Kontaktart | None = Field(default=None, description="Gibt die Kontaktart des Kontaktes an.")
    kontaktwert: str | None = Field(default=None, description="Die Nummer oder E-Mail-Adresse.", title="Kontaktwert")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
