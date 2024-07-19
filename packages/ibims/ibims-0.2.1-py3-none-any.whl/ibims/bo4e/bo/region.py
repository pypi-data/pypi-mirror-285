from pydantic import BaseModel, ConfigDict, Field

from ..com.regionskriterium import Regionskriterium
from ..enum.typ import Typ
from ..zusatz_attribut import ZusatzAttribut


class Region(BaseModel):
    """
    Modellierung einer Region als Menge von Kriterien, die eine Region beschreiben

    .. raw:: html

        <object data="../_static/images/bo4e/bo/Region.svg" type="image/svg+xml"></object>

    .. HINT::
        `Region JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/bo/Region.json>`_
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    id: str | None = Field(
        default=None,
        alias="_id",
        description="Hier können IDs anderer Systeme hinterlegt werden (z.B. eine SAP-GP-Nummer oder eine GUID)",
        title=" Id",
    )
    typ: Typ = Field(..., alias="_typ", description="Bezeichnung der Region")
    version: str = Field(
        ..., alias="_version", description='Version der BO-Struktur aka "fachliche Versionierung"', title=" Version"
    )
    bezeichnung: str | None = Field(default=None, description="Bezeichnung der Region", title="Bezeichnung")
    negativ_liste: list[Regionskriterium] | None = Field(
        default=None,
        alias="negativListe",
        description="Negativliste der Kriterien zur Definition der Region",
        title="Negativliste",
    )
    positiv_liste: list[Regionskriterium] | None = Field(
        default=None,
        alias="positivListe",
        description="Positivliste der Kriterien zur Definition der Region",
        title="Positivliste",
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
