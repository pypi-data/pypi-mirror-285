from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ..com.zaehlwerk import Zaehlwerk
from ..com.zeitraum import Zeitraum
from ..enum.messwerterfassung import Messwerterfassung
from ..enum.netzebene import Netzebene
from ..enum.registeranzahl import Registeranzahl
from ..enum.sparte import Sparte
from ..enum.typ import Typ
from ..enum.zaehlerauspraegung import Zaehlerauspraegung
from ..enum.zaehlergroesse import Zaehlergroesse
from ..enum.zaehlertyp import Zaehlertyp
from ..zusatz_attribut import ZusatzAttribut
from .geschaeftspartner import Geschaeftspartner


class ZaehlerGas(BaseModel):
    """
    Resolve some ambiguity of `Strom` and `Gas`
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    version: str | None = Field(default="v202401.2.1", alias="_version", title=" Version")
    typ: Typ | None = Field(default=Typ.ZAEHLERGAS, alias="_typ", title=" Typ")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Externereferenzen"
    )
    id: str | None = Field(default=None, alias="_id", title=" Id")
    zaehlernummer: str = Field(..., title="Zaehlernummer")
    sparte: Sparte
    zaehlerauspraegung: Zaehlerauspraegung | None = None
    zaehlertyp: Zaehlertyp
    zaehlwerke: list[Zaehlwerk] = Field(..., title="Zaehlwerke")
    tarifart: Registeranzahl | None = None
    zaehlerkonstante: Decimal | None = Field(default=None, title="Zaehlerkonstante")
    eichung_bis: datetime | None = Field(default=None, alias="eichungBis", title="Eichungbis")
    letzte_eichung: datetime | None = Field(default=None, alias="letzteEichung", title="Letzteeichung")
    zaehlerhersteller: Geschaeftspartner | None = None
    messwerterfassung: Messwerterfassung
    nachstes_ablesedatum: datetime | None = Field(
        default=None, alias="nachstesAblesedatum", title="Nachstesablesedatum"
    )
    aktiver_zeitraum: Zeitraum | None = Field(default=None, alias="aktiverZeitraum")
    zaehlergroesse: Zaehlergroesse
    druckniveau: Netzebene
