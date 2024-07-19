from pydantic import BaseModel, ConfigDict, Field

from ..com.adresse import Adresse
from ..com.geokoordinaten import Geokoordinaten
from ..com.katasteradresse import Katasteradresse
from ..com.messlokationszuordnung import Messlokationszuordnung
from ..com.verbrauch import Verbrauch
from ..com.zaehlwerk import Zaehlwerk
from ..enum.bilanzierungsmethode import Bilanzierungsmethode
from ..enum.energierichtung import Energierichtung
from ..enum.gasqualitaet import Gasqualitaet
from ..enum.gebiettyp import Gebiettyp
from ..enum.kundentyp import Kundentyp
from ..enum.marktgebiet import Marktgebiet
from ..enum.messtechnische_einordnung import MesstechnischeEinordnung
from ..enum.netzebene import Netzebene
from ..enum.profiltyp import Profiltyp
from ..enum.prognosegrundlage import Prognosegrundlage
from ..enum.regelzone import Regelzone
from ..enum.sparte import Sparte
from ..enum.typ import Typ
from ..enum.variant import Variant
from ..enum.verbrauchsart import Verbrauchsart
from ..zusatz_attribut import ZusatzAttribut
from .geschaeftspartner import Geschaeftspartner


class Marktlokation(BaseModel):
    """
    Object containing information about a Marktlokation

    .. raw:: html

        <object data="../_static/images/bo4e/bo/Marktlokation.svg" type="image/svg+xml"></object>

    .. HINT::
        `Marktlokation JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/bo/Marktlokation.json>`_
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
        ...,
        alias="_typ",
        description="Identifikationsnummer einer Marktlokation, an der Energie entweder verbraucht, oder erzeugt wird.",
    )
    version: str = Field(
        ..., alias="_version", description='Version der BO-Struktur aka "fachliche Versionierung"', title=" Version"
    )
    bilanzierungsgebiet: str | None = Field(
        default=None,
        description="Bilanzierungsgebiet, dem das Netzgebiet zugeordnet ist - im Falle eines Strom Netzes",
        title="Bilanzierungsgebiet",
    )
    bilanzierungsmethode: Bilanzierungsmethode | None = Field(
        default=None, description="Die Bilanzierungsmethode, RLM oder SLP"
    )
    endkunde: Geschaeftspartner | None = Field(
        default=None, description="Geschäftspartner, dem diese Marktlokation gehört"
    )
    energierichtung: Energierichtung | None = Field(
        default=None, description="Kennzeichnung, ob Energie eingespeist oder entnommen (ausgespeist) wird"
    )
    gasqualitaet: Gasqualitaet | None = Field(
        default=None, description="Die Gasqualität in diesem Netzgebiet. H-Gas oder L-Gas. Im Falle eines Gas-Netzes"
    )
    gebietstyp: Gebiettyp | None = Field(default=None, description="Typ des Netzgebietes, z.B. Verteilnetz")
    geoadresse: Geokoordinaten | None = Field(
        default=None, description='katasterinformation: Optional["Katasteradresse"] = None'
    )
    grundversorgercodenr: str | None = Field(
        default=None,
        description="Codenummer des Grundversorgers, der für diese Marktlokation zuständig ist",
        title="Grundversorgercodenr",
    )
    ist_unterbrechbar: bool | None = Field(
        default=None,
        alias="istUnterbrechbar",
        description="Gibt an, ob es sich um eine unterbrechbare Belieferung handelt",
        title="Istunterbrechbar",
    )
    katasterinformation: Katasteradresse | None = Field(
        default=None,
        description="Alternativ zu einer postalischen Adresse und Geokoordinaten kann hier eine Ortsangabe mittels Gemarkung und\nFlurstück erfolgen.",
    )
    kundengruppen: list[Kundentyp] | None = Field(
        default=None, description="Kundengruppen der Marktlokation", title="Kundengruppen"
    )
    lokationsadresse: Adresse | None = Field(
        default=None, description="Die Adresse, an der die Energie-Lieferung oder -Einspeisung erfolgt"
    )
    marktgebiet: Marktgebiet | None = None
    marktlokations_id: str = Field(
        ...,
        alias="marktlokationsId",
        description="Identifikationsnummer einer Marktlokation, an der Energie entweder verbraucht, oder erzeugt wird.",
        title="Marktlokationsid",
    )
    netzbetreibercodenr: str | None = Field(
        default=None,
        description="Codenummer des Netzbetreibers, an dessen Netz diese Marktlokation angeschlossen ist.",
        title="Netzbetreibercodenr",
    )
    netzebene: Netzebene | None = Field(
        default=None,
        description="Netzebene, in der der Bezug der Energie erfolgt.\nBei Strom Spannungsebene der Lieferung, bei Gas Druckstufe.\nBeispiel Strom: Niederspannung Beispiel Gas: Niederdruck.",
    )
    netzgebietsnr: str | None = Field(
        default=None, description="Die ID des Gebietes in der ene't-Datenbank", title="Netzgebietsnr"
    )
    regelzone: str | None = Field(default=None, description="Kundengruppen der Marktlokation", title="Regelzone")
    sparte: Sparte = Field(..., description="Sparte der Marktlokation, z.B. Gas oder Strom")
    verbrauchsart: Verbrauchsart | None = Field(default=None, description="Verbrauchsart der Marktlokation.")
    verbrauchsmengen: list[Verbrauch] | None = Field(default=None, title="Verbrauchsmengen")
    zaehlwerke: list[Zaehlwerk] | None = Field(
        default=None,
        description="für Gas. Code vom EIC, https://www.entsog.eu/data/data-portal/codes-list",
        title="Zaehlwerke",
    )
    zaehlwerke_der_beteiligten_marktrolle: list[Zaehlwerk] | None = Field(
        default=None, alias="zaehlwerkeDerBeteiligtenMarktrolle", title="Zaehlwerkederbeteiligtenmarktrolle"
    )
    zugehoerige_messlokation: Messlokationszuordnung | None = Field(default=None, alias="zugehoerigeMesslokation")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
    messtechnische_einordnung: MesstechnischeEinordnung = Field(..., alias="messtechnischeEinordnung")
    uebertragungsnetzgebiet: Regelzone | None = None
    variant: Variant
    community_id: str = Field(..., alias="communityId", title="Communityid")
    prognose_grundlage: Prognosegrundlage | None = Field(default=None, alias="prognoseGrundlage")
    prognose_grundlage_detail: Profiltyp | None = Field(default=None, alias="prognoseGrundlageDetail")
