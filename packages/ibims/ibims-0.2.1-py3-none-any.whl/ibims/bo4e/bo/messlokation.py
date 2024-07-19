from pydantic import BaseModel, ConfigDict, Field

from ..com.adresse import Adresse
from ..com.dienstleistung import Dienstleistung
from ..com.geokoordinaten import Geokoordinaten
from ..com.katasteradresse import Katasteradresse
from ..enum.netzebene import Netzebene
from ..enum.sparte import Sparte
from ..enum.typ import Typ
from ..zusatz_attribut import ZusatzAttribut
from .geraet import Geraet
from .zaehler import Zaehler


class Messlokation(BaseModel):
    """
    Object containing information about a Messlokation

    .. raw:: html

        <object data="../_static/images/bo4e/bo/Messlokation.svg" type="image/svg+xml"></object>

    .. HINT::
        `Messlokation JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/bo/Messlokation.json>`_
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
    typ: Typ = Field(
        ..., alias="_typ", description="Die Messlokations-Identifikation; Das ist die frühere Zählpunktbezeichnung"
    )
    version: str = Field(
        ..., alias="_version", description='Version der BO-Struktur aka "fachliche Versionierung"', title=" Version"
    )
    geoadresse: Geokoordinaten | None = Field(
        default=None, description='katasterinformation: Optional["Katasteradresse"] = None'
    )
    geraete: list[Geraet] | None = Field(
        default=None, description="Liste der Geräte, die zu dieser Messstelle gehört", title="Geraete"
    )
    grundzustaendiger_msb_codenr: str | None = Field(
        default=None,
        alias="grundzustaendigerMsbCodenr",
        description="grundzustaendiger_msbim_codenr: Optional[str] = None",
        title="Grundzustaendigermsbcodenr",
    )
    grundzustaendiger_msbim_codenr: str | None = Field(
        default=None,
        alias="grundzustaendigerMsbimCodenr",
        description='# only one of the following three optional address attributes can be set\nmessadresse: Optional["Adresse"] = None',
        title="Grundzustaendigermsbimcodenr",
    )
    katasterinformation: Katasteradresse | None = Field(
        default=None,
        description="Alternativ zu einer postalischen Adresse und Geokoordinaten kann hier eine Ortsangabe mittels Gemarkung und\nFlurstück erfolgen.",
    )
    messadresse: Adresse | None = Field(default=None, description='geoadresse: Optional["Geokoordinaten"] = None')
    messdienstleistung: list[Dienstleistung] | None = Field(
        default=None,
        description="Liste der Messdienstleistungen, die zu dieser Messstelle gehört",
        title="Messdienstleistung",
    )
    messgebietnr: str | None = Field(
        default=None, description="Die Nummer des Messgebietes in der ene't-Datenbank", title="Messgebietnr"
    )
    messlokations_id: str = Field(
        ...,
        alias="messlokationsId",
        description="Die Messlokations-Identifikation; Das ist die frühere Zählpunktbezeichnung",
        title="Messlokationsid",
    )
    messlokationszaehler: list[Zaehler] | None = Field(
        default=None, description="Zähler, die zu dieser Messlokation gehören", title="Messlokationszaehler"
    )
    netzebene_messung: Netzebene | None = Field(
        default=None, alias="netzebeneMessung", description="Spannungsebene der Messung"
    )
    sparte: Sparte | None = Field(default=None, description="Sparte der Messlokation, z.B. Gas oder Strom")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
