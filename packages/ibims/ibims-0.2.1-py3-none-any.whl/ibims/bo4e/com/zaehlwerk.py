from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..enum.abgabe_art import AbgabeArt
from ..enum.energierichtung import Energierichtung
from ..enum.mengeneinheit import Mengeneinheit
from ..enum.waermenutzung import Waermenutzung
from ..zusatz_attribut import ZusatzAttribut
from .konzessionsabgabe import Konzessionsabgabe
from .verwendungszweck_pro_marktrolle import VerwendungszweckProMarktrolle
from .zaehlzeitregister import Zaehlzeitregister


class Zaehlwerk(BaseModel):
    """
    Mit dieser Komponente werden Zählwerke modelliert.

    .. raw:: html

        <object data="../_static/images/bo4e/com/Zaehlwerk.svg" type="image/svg+xml"></object>

    .. HINT::
        `Zaehlwerk JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Zaehlwerk.json>`_
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
    anzahl_ablesungen: int | None = Field(
        default=None, alias="anzahlAblesungen", description="Abrechnungsrelevant", title="Anzahlablesungen"
    )
    bezeichnung: str | None = Field(default=None, title="Bezeichnung")
    einheit: Mengeneinheit | None = None
    ist_abrechnungsrelevant: bool | None = Field(
        default=None,
        alias="istAbrechnungsrelevant",
        description="Anzahl der Nachkommastellen",
        title="Istabrechnungsrelevant",
    )
    ist_schwachlastfaehig: bool | None = Field(
        default=None, alias="istSchwachlastfaehig", description="Schwachlastfaehigkeit", title="Istschwachlastfaehig"
    )
    ist_steuerbefreit: bool | None = Field(
        default=None, alias="istSteuerbefreit", description="Konzessionsabgabe", title="Iststeuerbefreit"
    )
    ist_unterbrechbar: bool | None = Field(
        default=None,
        alias="istUnterbrechbar",
        description="Stromverbrauchsart/Verbrauchsart Marktlokation",
        title="Istunterbrechbar",
    )
    konzessionsabgabe: Konzessionsabgabe | None = Field(default=None, description="Wärmenutzung Marktlokation")
    nachkommastelle: int | None = Field(default=None, description="Anzahl der Vorkommastellen", title="Nachkommastelle")
    obis_kennzahl: str = Field(..., alias="obisKennzahl", title="Obiskennzahl")
    richtung: Energierichtung | None = None
    verbrauchsart: str | None = Field(default=None, title="Verbrauchsart")
    verwendungszwecke: list[VerwendungszweckProMarktrolle] | None = Field(
        default=None, description="Schwachlastfaehigkeit", title="Verwendungszwecke"
    )
    vorkommastelle: int | None = Field(default=None, description="Steuerbefreiung", title="Vorkommastelle")
    waermenutzung: Waermenutzung | None = Field(default=None, description="Unterbrechbarkeit Marktlokation")
    wandlerfaktor: float | None = Field(default=None, title="Wandlerfaktor")
    zaehlwerk_id: str | None = Field(default=None, alias="zaehlwerkId", title="Zaehlwerkid")
    zaehlzeitregister: Zaehlzeitregister | None = Field(default=None, description="Anzahl Ablesungen pro Jahr")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
    vorkommastellen: int = Field(..., title="Vorkommastellen")
    nachkommastellen: int = Field(..., title="Nachkommastellen")
    schwachlastfaehig: bool = Field(..., title="Schwachlastfaehig")
    konzessionsabgaben_typ: AbgabeArt | None = Field(default=None, alias="konzessionsabgabenTyp")
    active_from: datetime = Field(..., alias="activeFrom", title="Activefrom")
    active_until: datetime | None = Field(default=None, alias="activeUntil", title="Activeuntil")
    description: str | None = Field(default=None, title="Description")
