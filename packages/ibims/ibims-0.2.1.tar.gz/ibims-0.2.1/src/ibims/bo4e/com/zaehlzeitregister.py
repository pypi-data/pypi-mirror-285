from pydantic import BaseModel, ConfigDict, Field

from ..zusatz_attribut import ZusatzAttribut


class Zaehlzeitregister(BaseModel):
    """
    Mit dieser Komponente werden Zählzeitregister modelliert. Ein Zählzeitregister beschreibt eine erweiterte Definition der Zählzeit
    in Bezug auf ein Register. Dabei werden alle Codes dazu vom Netzbetreiber vergeben.

    .. raw:: html

        <object data="../_static/images/bo4e/com/Zaehlzeitregister.svg" type="image/svg+xml"></object>

    .. HINT::
        `Zaehlzeitregister JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Zaehlzeitregister.json>`_
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
    ist_schwachlastfaehig: bool | None = Field(
        default=None, alias="istSchwachlastfaehig", description="Zählzeitregister", title="Istschwachlastfaehig"
    )
    zaehlzeit_definition: str | None = Field(
        default=None, alias="zaehlzeitDefinition", description="Zählzeitdefinition", title="Zaehlzeitdefinition"
    )
    zaehlzeit_register: str | None = Field(
        default=None, alias="zaehlzeitRegister", description="Zählzeitdefinition", title="Zaehlzeitregister"
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
