from pydantic import BaseModel, ConfigDict, Field

from ..enum.zaehlertyp import Zaehlertyp
from ..zusatz_attribut import ZusatzAttribut
from .adresse import Adresse
from .menge import Menge
from .zeitraum import Zeitraum


class Ausschreibungsdetail(BaseModel):
    """
    Die Komponente Ausschreibungsdetail wird verwendet um die Informationen zu einer Abnahmestelle innerhalb eines
    Ausschreibungsloses abzubilden.

    .. raw:: html

        <object data="../_static/images/bo4e/com/Ausschreibungsdetail.svg" type="image/svg+xml"></object>

    .. HINT::
        `Ausschreibungsdetail JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Ausschreibungsdetail.json>`_
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
    ist_lastgang_vorhanden: bool | None = Field(
        default=None,
        alias="istLastgangVorhanden",
        description="Prognosewert für die Jahresarbeit der ausgeschriebenen Lokation",
        title="Istlastgangvorhanden",
    )
    kunde: str | None = Field(
        default=None, description="Bezeichnung des Kunden, der die Marktlokation nutzt", title="Kunde"
    )
    lieferzeitraum: Zeitraum | None = Field(
        default=None, description="Angefragter Zeitraum für die ausgeschriebene Belieferung"
    )
    marktlokations_id: str | None = Field(
        default=None,
        alias="marktlokationsId",
        description="Identifikation einer ausgeschriebenen Marktlokation",
        title="Marktlokationsid",
    )
    marktlokationsadresse: Adresse | None = Field(
        default=None, description="Die Adresse an der die Marktlokation sich befindet"
    )
    marktlokationsbezeichnung: str | None = Field(
        default=None,
        description="Bezeichnung für die Lokation, z.B. 'Zentraler Einkauf, Hamburg'",
        title="Marktlokationsbezeichnung",
    )
    netzbetreiber: str | None = Field(
        default=None,
        description="Bezeichnung des zuständigen Netzbetreibers, z.B. 'Stromnetz Hamburg GmbH'",
        title="Netzbetreiber",
    )
    netzebene_lieferung: str | None = Field(
        default=None,
        alias="netzebeneLieferung",
        description="In der angegebenen Netzebene wird die Marktlokation versorgt, z.B. MSP für Mittelspannung",
        title="Netzebenelieferung",
    )
    netzebene_messung: str | None = Field(
        default=None,
        alias="netzebeneMessung",
        description="In der angegebenen Netzebene wird die Lokation gemessen, z.B. NSP für Niederspannung",
        title="Netzebenemessung",
    )
    prognose_arbeit_lieferzeitraum: Menge | None = Field(
        default=None,
        alias="prognoseArbeitLieferzeitraum",
        description="Ein Prognosewert für die Arbeit innerhalb des angefragten Lieferzeitraums der ausgeschriebenen Lokation",
    )
    prognose_jahresarbeit: Menge | None = Field(
        default=None,
        alias="prognoseJahresarbeit",
        description="Prognosewert für die Jahresarbeit der ausgeschriebenen Lokation",
    )
    prognose_leistung: Menge | None = Field(
        default=None,
        alias="prognoseLeistung",
        description="Prognosewert für die abgenommene maximale Leistung der ausgeschriebenen Lokation",
    )
    rechnungsadresse: Adresse | None = Field(default=None, description="Die (evtl. abweichende) Rechnungsadresse")
    zaehlernummer: str | None = Field(
        default=None, description="Die Bezeichnung des Zählers an der Marktlokation", title="Zaehlernummer"
    )
    zaehlertechnik: Zaehlertyp | None = Field(
        default=None,
        description="Spezifikation, um welche Zählertechnik es sich im vorliegenden Fall handelt, z.B. Leistungsmessung",
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
