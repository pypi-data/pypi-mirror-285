from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..com.betrag import Betrag
from ..com.rechnungsposition import Rechnungsposition
from ..com.steuerbetrag import Steuerbetrag
from ..com.zeitraum import Zeitraum
from ..enum.netznutzung_rechnungsart import NetznutzungRechnungsart
from ..enum.netznutzung_rechnungstyp import NetznutzungRechnungstyp
from ..enum.rechnungsstatus import Rechnungsstatus
from ..enum.rechnungstyp import Rechnungstyp
from ..enum.sparte import Sparte
from ..enum.typ import Typ
from ..zusatz_attribut import ZusatzAttribut
from .geschaeftspartner import Geschaeftspartner
from .marktlokation import Marktlokation
from .messlokation import Messlokation


class Rechnung(BaseModel):
    """
    Modell für die Abbildung von Rechnungen und Netznutzungsrechnungen im Kontext der Energiewirtschaft;

    .. raw:: html

        <object data="../_static/images/bo4e/bo/Rechnung.svg" type="image/svg+xml"></object>

    .. HINT::
        `Rechnung JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/bo/Rechnung.json>`_
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
    typ: Typ = Field(..., alias="_typ", description="Der Zeitraum der zugrunde liegenden Lieferung zur Rechnung")
    version: str = Field(
        ..., alias="_version", description='Version der BO-Struktur aka "fachliche Versionierung"', title=" Version"
    )
    faelligkeitsdatum: datetime | None = Field(
        default=None, description="Zu diesem Datum ist die Zahlung fällig", title="Faelligkeitsdatum"
    )
    gesamtbrutto: Betrag = Field(..., description="Die Summe aus Netto- und Steuerbetrag")
    gesamtnetto: Betrag | None = Field(default=None, description="Die Summe der Nettobeträge der Rechnungsteile")
    gesamtsteuer: Betrag = Field(..., description="Die Summe der Steuerbeträge der Rechnungsteile")
    ist_original: bool | None = Field(
        default=None,
        alias="istOriginal",
        description="Kennzeichen, ob es sich um ein Original (true) oder eine Kopie handelt (false)",
        title="Istoriginal",
    )
    ist_simuliert: bool | None = Field(
        default=None,
        alias="istSimuliert",
        description="Kennzeichen, ob es sich um eine simulierte Rechnung, z.B. zur Rechnungsprüfung handelt",
        title="Istsimuliert",
    )
    ist_storno: bool | None = Field(
        default=None,
        alias="istStorno",
        description="Eine im Verwendungskontext eindeutige Nummer für die Rechnung",
        title="Iststorno",
    )
    marktlokation: Marktlokation | None = Field(
        default=None, description="Marktlokation, auf die sich die Rechnung bezieht"
    )
    messlokation: Messlokation | None = Field(
        default=None, description="Messlokation, auf die sich die Rechnung bezieht"
    )
    netznutzungrechnungsart: NetznutzungRechnungsart | None = Field(
        default=None, description="Aus der INVOIC entnommen, befüllt wenn es sich um eine Netznutzungsrechnung handelt"
    )
    netznutzungrechnungstyp: NetznutzungRechnungstyp | None = Field(
        default=None, description="Aus der INVOIC entnommen, befüllt wenn es sich um eine Netznutzungsrechnung handelt"
    )
    original_rechnungsnummer: str | None = Field(
        default=None,
        alias="originalRechnungsnummer",
        description="Im Falle einer Stornorechnung (storno = true) steht hier die Rechnungsnummer der stornierten Rechnung",
        title="Originalrechnungsnummer",
    )
    rabatt_brutto: Betrag | None = Field(
        default=None, alias="rabattBrutto", description="Gesamtrabatt auf den Bruttobetrag"
    )
    rechnungsdatum: datetime | None = Field(
        default=None, description="Ausstellungsdatum der Rechnung", title="Rechnungsdatum"
    )
    rechnungsempfaenger: Geschaeftspartner | None = Field(
        default=None,
        description="Der Aussteller der Rechnung, die Rollencodenummer kennt man über den im Geschäftspartner verlinkten Marktteilnehmer",
    )
    rechnungsersteller: Geschaeftspartner | None = Field(
        default=None,
        description="Der Aussteller der Rechnung, die Rollencodenummer kennt man über den im Geschäftspartner verlinkten Marktteilnehmer",
    )
    rechnungsnummer: str | None = Field(
        default=None,
        description="Eine im Verwendungskontext eindeutige Nummer für die Rechnung",
        title="Rechnungsnummer",
    )
    rechnungsperiode: Zeitraum | None = Field(
        default=None, description="Der Zeitraum der zugrunde liegenden Lieferung zur Rechnung"
    )
    rechnungspositionen: list[Rechnungsposition] | None = Field(
        default=None, description="Die Rechnungspositionen", title="Rechnungspositionen"
    )
    rechnungsstatus: Rechnungsstatus | None = Field(
        default=None, description="Status der Rechnung zur Kennzeichnung des Bearbeitungsstandes"
    )
    rechnungstitel: str | None = Field(
        default=None, description="Bezeichnung für die vorliegende Rechnung", title="Rechnungstitel"
    )
    rechnungstyp: Rechnungstyp = Field(..., description="Ein kontextbezogender Rechnungstyp, z.B. Netznutzungsrechnung")
    sparte: Sparte | None = Field(
        default=None, description="Sparte (Strom, Gas ...) für die die Rechnung ausgestellt ist"
    )
    steuerbetraege: list[Steuerbetrag] | None = Field(
        default=None, description="Sparte (Strom, Gas ...) für die die Rechnung ausgestellt ist", title="Steuerbetraege"
    )
    vorausgezahlt: Betrag | None = Field(
        default=None, description="Die Summe evtl. vorausgezahlter Beträge, z.B. Abschläge. Angabe als Bruttowert"
    )
    zu_zahlen: Betrag | None = Field(
        default=None,
        alias="zuZahlen",
        description="Der zu zahlende Betrag, der sich aus (gesamtbrutto - vorausbezahlt - rabattBrutto) ergibt",
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
    ist_selbstausgestellt: bool | None = Field(default=None, alias="istSelbstausgestellt", title="Istselbstausgestellt")
    ist_reverse_charge: bool | None = Field(default=None, alias="istReverseCharge", title="Istreversecharge")
