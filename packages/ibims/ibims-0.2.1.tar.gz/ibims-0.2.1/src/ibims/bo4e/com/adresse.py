from pydantic import BaseModel, ConfigDict, Field

from ..enum.landescode import Landescode
from ..zusatz_attribut import ZusatzAttribut


class Adresse(BaseModel):
    """
    Contains an address that can be used for most purposes.

    .. raw:: html

        <object data="../_static/images/bo4e/com/Adresse.svg" type="image/svg+xml"></object>

    .. HINT::
        `Adresse JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Adresse.json>`_
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
    adresszusatz: str | None = Field(
        default=None,
        description='Zusatzhinweis zum Auffinden der Adresse, z.B. "3. Stock linke Wohnung"',
        title="Adresszusatz",
    )
    co_ergaenzung: str | None = Field(
        default=None,
        alias="coErgaenzung",
        description='Im Falle einer c/o-Adresse steht in diesem Attribut die Anrede. Z.B. "c/o Veronica Hauptmieterin"',
        title="Coergaenzung",
    )
    hausnummer: str | None = Field(
        default=None, description='Hausnummer inkl. Zusatz; z.B. "3", "4a"', title="Hausnummer"
    )
    landescode: Landescode | None = Field(default=Landescode.DE, description="Offizieller ISO-Landescode")
    ort: str = Field(..., description='Bezeichnung der Stadt; z.B. "Hückelhoven"', title="Ort")
    ortsteil: str | None = Field(default=None, description='Bezeichnung des Ortsteils; z.B. "Mitte"', title="Ortsteil")
    postfach: str | None = Field(
        default=None,
        description="Im Falle einer Postfachadresse das Postfach; Damit werden Straße und Hausnummer nicht berücksichtigt",
        title="Postfach",
    )
    postleitzahl: str = Field(..., description='Die Postleitzahl; z.B: "41836"', title="Postleitzahl")
    strasse: str | None = Field(default=None, description='Bezeichnung der Straße; z.B. "Weserstraße"', title="Strasse")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
