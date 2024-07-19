from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ..enum.steuerkennzeichen import Steuerkennzeichen
from ..enum.waehrungscode import Waehrungscode
from ..zusatz_attribut import ZusatzAttribut


class Steuerbetrag(BaseModel):
    """
    Abbildung eines Steuerbetrages.

    .. raw:: html

        <object data="../_static/images/bo4e/com/Steuerbetrag.svg" type="image/svg+xml"></object>

    .. HINT::
        `Steuerbetrag JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Steuerbetrag.json>`_
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
    basiswert: float = Field(
        ..., description="Nettobetrag für den die Steuer berechnet wurde. Z.B. 100", title="Basiswert"
    )
    steuerkennzeichen: Steuerkennzeichen | None = Field(
        default=None, description="Kennzeichnung des Steuersatzes, bzw. Verfahrens."
    )
    steuerwert: float = Field(
        ..., description="Aus dem Basiswert berechnete Steuer. Z.B. 19 (bei UST_19)", title="Steuerwert"
    )
    waehrung: Waehrungscode | None = Field(default=None, description="Währung. Z.B. Euro.")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
    steuerwert_vorausgezahlt: Decimal | None = Field(
        default=None, alias="steuerwertVorausgezahlt", title="Steuerwertvorausgezahlt"
    )
