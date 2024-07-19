from pydantic import BaseModel, ConfigDict, Field

from ..enum.bdew_artikelnummer import BDEWArtikelnummer
from ..enum.bemessungsgroesse import Bemessungsgroesse
from ..enum.kalkulationsmethode import Kalkulationsmethode
from ..enum.leistungstyp import Leistungstyp
from ..enum.mengeneinheit import Mengeneinheit
from ..enum.steuerkennzeichen import Steuerkennzeichen
from ..enum.tarifzeit import Tarifzeit
from ..enum.waehrungseinheit import Waehrungseinheit
from ..zusatz_attribut import ZusatzAttribut
from .preisstaffel import Preisstaffel


class Preisposition(BaseModel):
    """
    Preis für eine definierte Lieferung oder Leistung innerhalb eines Preisblattes

    .. raw:: html

        <object data="../_static/images/bo4e/com/Preisposition.svg" type="image/svg+xml"></object>

    .. HINT::
        `Preisposition JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Preisposition.json>`_
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
    bdew_artikelnummer: BDEWArtikelnummer | None = Field(
        default=None,
        alias="bdewArtikelnummer",
        description="Mit der Menge der hier angegebenen Größe wird die Staffelung/Zonung durchgeführt. Z.B. Vollbenutzungsstunden",
    )
    berechnungsmethode: Kalkulationsmethode | None = Field(
        default=None, description="Das Modell, das der Preisbildung zugrunde liegt"
    )
    bezugsgroesse: Mengeneinheit | None = Field(
        default=None,
        description="Hier wird festgelegt, auf welche Bezugsgrösse sich der Preis bezieht, z.B. kWh oder Stück",
    )
    freimenge_blindarbeit: float | None = Field(
        default=None,
        alias="freimengeBlindarbeit",
        description="Der Anteil der Menge der Blindarbeit in Prozent von der Wirkarbeit, für die keine Abrechnung erfolgt",
        title="Freimengeblindarbeit",
    )
    freimenge_leistungsfaktor: float | None = Field(
        default=None,
        alias="freimengeLeistungsfaktor",
        description="gruppenartikel_id: Optional[str] = None",
        title="Freimengeleistungsfaktor",
    )
    gruppenartikel_id: str | None = Field(
        default=None,
        alias="gruppenartikelId",
        description="Übergeordnete Gruppen-ID, die sich ggf. auf die Artikel-ID in der Preisstaffel bezieht",
        title="Gruppenartikelid",
    )
    leistungsbezeichnung: str | None = Field(
        default=None,
        description="Bezeichnung für die in der Position abgebildete Leistungserbringung",
        title="Leistungsbezeichnung",
    )
    leistungstyp: Leistungstyp | None = Field(
        default=None, description="Standardisierte Bezeichnung für die abgerechnete Leistungserbringung"
    )
    preiseinheit: Waehrungseinheit | None = Field(
        default=None, description="Festlegung, mit welcher Preiseinheit abgerechnet wird, z.B. Ct. oder €"
    )
    preisstaffeln: list[Preisstaffel] = Field(
        ..., description="Preisstaffeln, die zu dieser Preisposition gehören", title="Preisstaffeln"
    )
    tarifzeit: Tarifzeit | None = Field(
        default=None, description="Festlegung, für welche Tarifzeit der Preis hier festgelegt ist"
    )
    zeitbasis: Mengeneinheit | None = Field(
        default=None, description="Festlegung, für welche Tarifzeit der Preis hier festgelegt ist"
    )
    zonungsgroesse: Bemessungsgroesse | None = Field(
        default=None,
        description="Mit der Menge der hier angegebenen Größe wird die Staffelung/Zonung durchgeführt. Z.B. Vollbenutzungsstunden",
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
    steuersatz: Steuerkennzeichen
