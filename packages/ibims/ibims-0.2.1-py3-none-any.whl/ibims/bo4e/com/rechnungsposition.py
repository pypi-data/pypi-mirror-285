from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..enum.bdew_artikelnummer import BDEWArtikelnummer
from ..enum.mengeneinheit import Mengeneinheit
from ..zusatz_attribut import ZusatzAttribut
from .betrag import Betrag
from .menge import Menge
from .preis import Preis
from .steuerbetrag import Steuerbetrag


class Rechnungsposition(BaseModel):
    """
    Über Rechnungspositionen werden Rechnungen strukturiert.
    In einem Rechnungsteil wird jeweils eine in sich geschlossene Leistung abgerechnet.

    .. raw:: html

        <object data="../_static/images/bo4e/com/Rechnungsposition.svg" type="image/svg+xml"></object>

    .. HINT::
        `Rechnungsposition JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Rechnungsposition.json>`_
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
    artikel_id: str | None = Field(
        default=None,
        alias="artikelId",
        description="Standardisierte vom BDEW herausgegebene Liste, welche im Strommarkt die BDEW-Artikelnummer ablöst",
        title="Artikelid",
    )
    artikelnummer: BDEWArtikelnummer | None = Field(
        default=None, description="Kennzeichnung der Rechnungsposition mit der Standard-Artikelnummer des BDEW"
    )
    einzelpreis: Preis | None = Field(default=None, description="Der Preis für eine Einheit der energetischen Menge")
    lieferung_bis: datetime | None = Field(
        default=None,
        alias="lieferungBis",
        description="Ende der Lieferung für die abgerechnete Leistung (exklusiv)",
        title="Lieferungbis",
    )
    lieferung_von: datetime | None = Field(
        default=None,
        alias="lieferungVon",
        description="Start der Lieferung für die abgerechnete Leistung (inklusiv)",
        title="Lieferungvon",
    )
    lokations_id: str | None = Field(
        default=None,
        alias="lokationsId",
        description="Marktlokation, die zu dieser Position gehört",
        title="Lokationsid",
    )
    positions_menge: Menge = Field(..., alias="positionsMenge", description="Die abgerechnete Menge mit Einheit")
    positionsnummer: int | None = Field(
        default=None, description="Fortlaufende Nummer für die Rechnungsposition", title="Positionsnummer"
    )
    positionstext: str | None = Field(
        default=None, description="Bezeichung für die abgerechnete Position", title="Positionstext"
    )
    teilrabatt_netto: Betrag | None = Field(
        default=None, alias="teilrabattNetto", description="Nettobetrag für den Rabatt dieser Position"
    )
    teilsumme_netto: Betrag = Field(
        ...,
        alias="teilsummeNetto",
        description='# the cross check in general doesn\'t work because Betrag and Preis use different enums to describe the currency\n# see https://github.com/Hochfrequenz/BO4E-python/issues/126\n\n#: Auf die Position entfallende Steuer, bestehend aus Steuersatz und Betrag\nteilsumme_steuer: Optional["Steuerbetrag"] = None\n\n#: Falls sich der Preis auf eine Zeit bezieht, steht hier die Einheit\nzeiteinheit: Optional["Mengeneinheit"] = None\n\n#: Kennzeichnung der Rechnungsposition mit der Standard-Artikelnummer des BDEW\nartikelnummer: Optional["BDEWArtikelnummer"] = None\n#: Marktlokation, die zu dieser Position gehört\nlokations_id: Optional[str] = None\n\nzeitbezogene_menge: Optional["Menge"] = None',
    )
    teilsumme_steuer: Steuerbetrag = Field(
        ...,
        alias="teilsummeSteuer",
        description="Auf die Position entfallende Steuer, bestehend aus Steuersatz und Betrag",
    )
    zeitbezogene_menge: Menge | None = Field(
        default=None, alias="zeitbezogeneMenge", description="Nettobetrag für den Rabatt dieser Position"
    )
    zeiteinheit: Mengeneinheit | None = Field(
        default=None, description="Falls sich der Preis auf eine Zeit bezieht, steht hier die Einheit"
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
