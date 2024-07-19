from pydantic import BaseModel, ConfigDict, Field

from ..zusatz_attribut import ZusatzAttribut


class Sigmoidparameter(BaseModel):
    """
    Die Sigmoid-Funktion, beispielsweise zur Berechnung eines Leistungspreises hat die Form:
    LP=A/(1+(P/B)^C)+D

    .. raw:: html

        <object data="../_static/images/bo4e/com/Sigmoidparameter.svg" type="image/svg+xml"></object>

    .. HINT::
        `Sigmoidparameter JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Sigmoidparameter.json>`_
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    a: float | None = Field(default=None, alias="A", description="Briefmarke Ortsverteilnetz (EUR/kWh)", title="A")
    b: float | None = Field(default=None, alias="B", description="Briefmarke Ortsverteilnetz (EUR/kWh)", title="B")
    c: float | None = Field(default=None, alias="C", description="Wendepunkt für die bepreiste Menge (kW)", title="C")
    d: float | None = Field(default=None, alias="D", description="Exponent (einheitenlos)", title="D")
    id: str | None = Field(
        default=None,
        alias="_id",
        description='zusatz_attribute: Optional[list["ZusatzAttribut"]] = None\n\n# pylint: disable=duplicate-code\nmodel_config = ConfigDict(\n    alias_generator=camelize,\n    populate_by_name=True,\n    extra="allow",\n    # json_encoders is deprecated, but there is no easy-to-use alternative. The best way would be to create\n    # an annotated version of Decimal, but you would have to use it everywhere in the pydantic models.\n    # See this issue for more info: https://github.com/pydantic/pydantic/issues/6375\n    json_encoders={Decimal: str},\n)',
        title=" Id",
    )
    version: str = Field(
        ..., alias="_version", description='Version der BO-Struktur aka "fachliche Versionierung"', title=" Version"
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
