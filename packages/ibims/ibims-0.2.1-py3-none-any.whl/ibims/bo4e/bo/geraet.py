from pydantic import BaseModel, ConfigDict, Field

from ..enum.geraeteklasse import Geraeteklasse
from ..enum.geraetetyp import Geraetetyp
from ..enum.typ import Typ
from ..zusatz_attribut import ZusatzAttribut


class Geraet(BaseModel):
    """
    Mit diesem BO werden alle Geräte modelliert, die keine Zähler sind.

    .. raw:: html

        <object data="../_static/images/bo4e/bo/Geraet.svg" type="image/svg+xml"></object>

    .. HINT::
        `Geraet JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/bo/Geraet.json>`_
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
    typ: Typ = Field(..., alias="_typ", description="Die auf dem Gerät aufgedruckte Nummer, die vom MSB vergeben wird.")
    version: str = Field(
        ..., alias="_version", description='Version der BO-Struktur aka "fachliche Versionierung"', title=" Version"
    )
    bezeichnung: str | None = Field(default=None, description="Bezeichnung des Geräts", title="Bezeichnung")
    geraeteklasse: Geraeteklasse | None = Field(
        default=None, description="Die übergreifende Klasse eines Geräts, beispielsweise Wandler"
    )
    geraetenummer: str | None = Field(
        default=None,
        description="Die auf dem Gerät aufgedruckte Nummer, die vom MSB vergeben wird.",
        title="Geraetenummer",
    )
    geraetetyp: Geraetetyp | None = Field(
        default=None, description="Der speziellere Typ eines Gerätes, beispielsweise Stromwandler"
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
