from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..com.adresse import Adresse
from ..com.kontaktweg import Kontaktweg
from ..com.zustaendigkeit import Zustaendigkeit
from ..enum.anrede import Anrede
from ..enum.titel import Titel
from ..enum.typ import Typ
from ..zusatz_attribut import ZusatzAttribut


class Person(BaseModel):
    """
    Object containing information about a Person

    .. raw:: html

        <object data="../_static/images/bo4e/bo/Person.svg" type="image/svg+xml"></object>

    .. HINT::
        `Person JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/bo/Person.json>`_
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
    adresse: Adresse | None = Field(
        default=None, description="Adresse der Person, falls diese von der Adresse des Geschäftspartners abweicht"
    )
    anrede: Anrede | None = Field(default=None, description="Mögliche Anrede der Person")
    geburtsdatum: datetime | None = Field(default=None, description="Geburtsdatum der Person", title="Geburtsdatum")
    individuelle_anrede: str | None = Field(
        default=None,
        alias="individuelleAnrede",
        description='Im Falle einer nicht standardisierten Anrede kann hier eine frei definierbare Anrede vorgegeben werden.\nBeispiel: "Vereinsgemeinschaft", "Pfarrer", "Hochwürdigster Herr Abt".',
        title="Individuelleanrede",
    )
    kommentar: str | None = Field(default=None, description="Weitere Informationen zur Person", title="Kommentar")
    kontaktwege: list[Kontaktweg] | None = Field(
        default=None, description="Kontaktwege der Person", title="Kontaktwege"
    )
    nachname: str | None = Field(default=None, description="Nachname (Familienname) der Person", title="Nachname")
    titel: Titel | None = Field(default=None, description="Möglicher Titel der Person")
    vorname: str | None = Field(default=None, description="Vorname der Person", title="Vorname")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
    zustaendigkeiten: list[Zustaendigkeit] | None = Field(
        default=None, description="Liste der Abteilungen und Zuständigkeiten der Person", title="Zustaendigkeiten"
    )
