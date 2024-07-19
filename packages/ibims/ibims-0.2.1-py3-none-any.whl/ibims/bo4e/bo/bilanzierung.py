from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..com.lastprofil import Lastprofil
from ..enum.aggregationsverantwortung import Aggregationsverantwortung
from ..enum.profiltyp import Profiltyp
from ..enum.prognosegrundlage import Prognosegrundlage
from ..enum.typ import Typ
from ..zusatz_attribut import ZusatzAttribut


class Bilanzierung(BaseModel):
    """
    Bilanzierung is a business object used for balancing. This object is no BO4E standard and a complete go
    implementation can be found at
    https://github.com/Hochfrequenz/go-bo4e/blob/3414a1eac741542628df796d6beb43eaa27b0b3e/bo/bilanzierung.go
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    version: str | None = Field(default="v202401.2.1", alias="_version", title=" Version")
    typ: Typ | None = Field(default=Typ.BILANZIERUNG, alias="_typ", title=" Typ")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="ZusatzAttribute"
    )
    id: str | None = Field(default=None, alias="_id", title=" Id")
    bilanzierungsbeginn: datetime = Field(..., title="Bilanzierungsbeginn")
    bilanzierungsende: datetime = Field(..., title="Bilanzierungsende")
    bilanzkreis: str | None = Field(default=None, title="Bilanzkreis")
    aggregationsverantwortung: Aggregationsverantwortung | None = None
    lastprofile: list[Lastprofil] | None = Field(default=None, title="Lastprofile")
    prognosegrundlage: Prognosegrundlage | None = None
    details_prognosegrundlage: Profiltyp | None = Field(default=None, alias="detailsPrognosegrundlage")
    lastprofil_namen: list[str] | None = Field(default=None, alias="lastprofilNamen")
