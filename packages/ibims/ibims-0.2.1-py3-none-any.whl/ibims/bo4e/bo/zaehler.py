from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..com.zaehlwerk import Zaehlwerk
from ..com.zeitraum import Zeitraum
from ..enum.befestigungsart import Befestigungsart
from ..enum.messwerterfassung import Messwerterfassung
from ..enum.registeranzahl import Registeranzahl
from ..enum.sparte import Sparte
from ..enum.typ import Typ
from ..enum.zaehlerauspraegung import Zaehlerauspraegung
from ..enum.zaehlergroesse import Zaehlergroesse
from ..enum.zaehlertyp import Zaehlertyp
from ..enum.zaehlertyp_spezifikation import ZaehlertypSpezifikation
from ..zusatz_attribut import ZusatzAttribut
from .geraet import Geraet
from .geschaeftspartner import Geschaeftspartner


class Zaehler(BaseModel):
    """
    Object containing information about a meter/"Zaehler".

    .. raw:: html

        <object data="../_static/images/bo4e/bo/Zaehler.svg" type="image/svg+xml"></object>

    .. HINT::
        `Zaehler JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/bo/Zaehler.json>`_
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
    typ: Typ = Field(..., alias="_typ", description="Typisierung des Zählers")
    version: str = Field(
        ..., alias="_version", description='Version der BO-Struktur aka "fachliche Versionierung"', title=" Version"
    )
    befestigungsart: Befestigungsart | None = Field(default=None, description="Besondere Spezifikation des Zählers")
    eichung_bis: datetime | None = Field(
        default=None, alias="eichungBis", description="Zählerkonstante auf dem Zähler", title="Eichungbis"
    )
    geraete: list[Geraet] | None = Field(default=None, description="Größe des Zählers", title="Geraete")
    ist_fernschaltbar: bool | None = Field(
        default=None, alias="istFernschaltbar", description="Der Hersteller des Zählers", title="Istfernschaltbar"
    )
    letzte_eichung: datetime | None = Field(
        default=None,
        alias="letzteEichung",
        description="Bis zu diesem Datum (exklusiv) ist der Zähler geeicht.",
        title="Letzteeichung",
    )
    messwerterfassung: Messwerterfassung | None = Field(default=None, title="Messwerterfassung")
    registeranzahl: Registeranzahl | None = Field(
        default=None, description="Spezifikation bezüglich unterstützter Tarif"
    )
    sparte: Sparte = Field(..., description="Nummerierung des Zählers,vergeben durch den Messstellenbetreiber")
    zaehlerauspraegung: Zaehlerauspraegung | None = Field(default=None, description="Strom oder Gas")
    zaehlergroesse: Zaehlergroesse | None = Field(default=None, description="Befestigungsart")
    zaehlerhersteller: Geschaeftspartner | None = Field(default=None, description="Der Hersteller des Zählers")
    zaehlerkonstante: float | None = Field(
        default=None, description="Spezifikation bezüglich unterstützter Tarif", title="Zaehlerkonstante"
    )
    zaehlernummer: str = Field(
        ..., description="Nummerierung des Zählers,vergeben durch den Messstellenbetreiber", title="Zaehlernummer"
    )
    zaehlertyp: Zaehlertyp | None = Field(default=None, description="Spezifikation die Richtung des Zählers betreffend")
    zaehlertyp_spezifikation: ZaehlertypSpezifikation | None = Field(
        default=None, alias="zaehlertypSpezifikation", description="Messwerterfassung des Zählers"
    )
    zaehlwerke: list[Zaehlwerk] = Field(..., description="Typisierung des Zählers", title="Zaehlwerke")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
    nachstes_ablesedatum: datetime | None = Field(
        default=None, alias="nachstesAblesedatum", title="Nachstesablesedatum"
    )
    aktiver_zeitraum: Zeitraum | None = Field(default=None, alias="aktiverZeitraum")
