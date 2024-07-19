from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..com.adresse import Adresse
from ..com.kontaktweg import Kontaktweg
from ..enum.anrede import Anrede
from ..enum.geschaeftspartnerrolle import Geschaeftspartnerrolle
from ..enum.organisationstyp import Organisationstyp
from ..enum.titel import Titel
from ..enum.typ import Typ
from ..zusatz_attribut import ZusatzAttribut
from .person import Person


class Geschaeftspartner(BaseModel):
    """
    Mit diesem Objekt können Geschäftspartner übertragen werden.
    Sowohl Unternehmen, als auch Privatpersonen können Geschäftspartner sein.
    Hinweis: "Marktteilnehmer" haben ein eigenes BO, welches sich von diesem BO ableitet.
    Hier sollte daher keine Zuordnung zu Marktrollen erfolgen.

    .. raw:: html

        <object data="../_static/images/bo4e/bo/Geschaeftspartner.svg" type="image/svg+xml"></object>

    .. HINT::
        `Geschaeftspartner JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/bo/Geschaeftspartner.json>`_
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
    typ: Typ = Field(..., alias="_typ", description="Mögliche Anrede der Person")
    version: str = Field(
        ..., alias="_version", description='Version der BO-Struktur aka "fachliche Versionierung"', title=" Version"
    )
    adresse: Adresse | None = Field(default=None, description="Adresse des Geschäftspartners")
    amtsgericht: str | None = Field(
        default=None,
        description="Amtsgericht bzw Handelsregistergericht, das die Handelsregisternummer herausgegeben hat",
        title="Amtsgericht",
    )
    anrede: Anrede | None = Field(default=None, description="Mögliche Anrede der Person")
    ansprechpartner: list[Person] | None = Field(default=None, title="Ansprechpartner")
    geschaeftspartnerrollen: list[Geschaeftspartnerrolle] | None = Field(
        default=None,
        description="Rollen, die die Geschäftspartner inne haben (z.B. Interessent, Kunde)",
        title="Geschaeftspartnerrollen",
    )
    glaeubiger_id: str | None = Field(
        default=None,
        alias="glaeubigerId",
        description='Die Gläubiger-ID welche im Zahlungsverkehr verwendet wird; Z.B. "DE 47116789"',
        title="Glaeubigerid",
    )
    handelsregisternummer: str | None = Field(
        default=None, description="Handelsregisternummer des Geschäftspartners", title="Handelsregisternummer"
    )
    individuelle_anrede: str | None = Field(
        default=None,
        alias="individuelleAnrede",
        description='Im Falle einer nicht standardisierten Anrede kann hier eine frei definierbare Anrede vorgegeben werden.\nBeispiel: "Vereinsgemeinschaft", "Pfarrer", "Hochwürdigster Herr Abt".',
        title="Individuelleanrede",
    )
    kontaktwege: list[Kontaktweg] | None = Field(
        default=None, description="Kontaktwege des Geschäftspartners", title="Kontaktwege"
    )
    nachname: str | None = Field(default=None, description="Nachname (Familienname) der Person", title="Nachname")
    organisationsname: str | None = Field(
        default=None, description="Kontaktwege des Geschäftspartners", title="Organisationsname"
    )
    organisationstyp: Organisationstyp | None = Field(
        default=None, description="organisationsname: Optional[str] = None"
    )
    titel: Titel | None = Field(default=None, description="Möglicher Titel der Person")
    umsatzsteuer_id: str | None = Field(
        default=None,
        alias="umsatzsteuerId",
        description='Die Steuer-ID des Geschäftspartners; Beispiel: "DE 813281825"',
        title="Umsatzsteuerid",
    )
    vorname: str | None = Field(default=None, description="Vorname der Person", title="Vorname")
    website: str | None = Field(default=None, description="Internetseite des Marktpartners", title="Website")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
    erstellungsdatum: datetime | None = Field(default=None, title="Erstellungsdatum")
    geburtstag: datetime | None = Field(default=None, title="Geburtstag")
    telefonnummer_mobil: str | None = Field(default=None, alias="telefonnummerMobil", title="Telefonnummermobil")
    telefonnummer_privat: str | None = Field(default=None, alias="telefonnummerPrivat", title="Telefonnummerprivat")
    telefonnummer_geschaeft: str | None = Field(
        default=None, alias="telefonnummerGeschaeft", title="Telefonnummergeschaeft"
    )
    firmenname: str | None = Field(default=None, title="Firmenname")
    hausbesitzer: bool | None = Field(default=None, title="Hausbesitzer")
