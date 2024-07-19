from pydantic import BaseModel, ConfigDict, Field

from ..enum.marktrolle import Marktrolle
from ..enum.rollencodetyp import Rollencodetyp
from ..enum.sparte import Sparte
from ..enum.typ import Typ
from ..zusatz_attribut import ZusatzAttribut
from .geschaeftspartner import Geschaeftspartner


class Marktteilnehmer(BaseModel):
    """
    Objekt zur Aufnahme der Information zu einem Marktteilnehmer

    .. raw:: html

        <object data="../_static/images/bo4e/bo/Marktteilnehmer.svg" type="image/svg+xml"></object>

    .. HINT::
        `Marktteilnehmer JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/bo/Marktteilnehmer.json>`_
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
    typ: Typ = Field(..., alias="_typ", description="Gibt im Klartext die Bezeichnung der Marktrolle an")
    version: str = Field(
        ..., alias="_version", description='Version der BO-Struktur aka "fachliche Versionierung"', title=" Version"
    )
    geschaeftspartner: Geschaeftspartner | None = Field(
        default=None, description="Der zu diesem Marktteilnehmer gehörende Geschäftspartner"
    )
    makoadresse: list[str] | None = Field(
        default=None,
        description="Die 1:1-Kommunikationsadresse des Marktteilnehmers. Diese wird in der Marktkommunikation verwendet. Konkret kann dies eine eMail-Adresse oder ein AS4-Endpunkt sein.",
        title="Makoadresse",
    )
    marktrolle: Marktrolle | None = Field(
        default=None, description="Gibt im Klartext die Bezeichnung der Marktrolle an"
    )
    rollencodenummer: str | None = Field(
        default=None, description="Gibt die Codenummer der Marktrolle an", title="Rollencodenummer"
    )
    rollencodetyp: Rollencodetyp | None = Field(default=None, description="Gibt den Typ des Codes an")
    sparte: Sparte | None = Field(default=None, description="Sparte des Marktteilnehmers, z.B. Gas oder Strom")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
