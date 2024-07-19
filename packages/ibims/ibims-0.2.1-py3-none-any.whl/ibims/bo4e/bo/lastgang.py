from pydantic import BaseModel, ConfigDict, Field

from ..com.menge import Menge
from ..com.zeitreihenwert import Zeitreihenwert
from ..enum.mengeneinheit import Mengeneinheit
from ..enum.sparte import Sparte
from ..enum.typ import Typ
from ..zusatz_attribut import ZusatzAttribut
from .marktlokation import Marktlokation
from .messlokation import Messlokation


class Lastgang(BaseModel):
    """
    Modell zur Abbildung eines Lastganges;
    In diesem Modell werden die Messwerte mit einem vollständigen Zeitintervall (zeit_intervall_laenge) angegeben und es bietet daher eine hohe Flexibilität in der Übertragung jeglicher zeitlich veränderlicher Messgrössen.

    .. raw:: html

        <object data="../_static/images/bo4e/bo/Lastgang.svg" type="image/svg+xml"></object>

    .. HINT::
        `Lastgang JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/bo/Lastgang.json>`_
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
    typ: Typ = Field(..., alias="_typ", description="Angabe, ob es sich um einen Gas- oder Stromlastgang handelt")
    marktlokation: Marktlokation | None = Field(default=None, description="Marktlokation, zu der der Lastgang gehört")
    messgroesse: Mengeneinheit | None = Field(
        default=None, description="Definition der gemessenen Größe anhand ihrer Einheit"
    )
    messlokation: Messlokation | None = Field(default=None, description="Marktlokation, zu der der Lastgang gehört")
    obis_kennzahl: str | None = Field(
        default=None,
        alias="obisKennzahl",
        description="Die OBIS-Kennzahl für den Wert, die festlegt, welche Größe mit dem Stand gemeldet wird, z.B. '1-0:1.8.1'",
        title="Obiskennzahl",
    )
    sparte: Sparte | None = Field(
        default=None, description="Angabe, ob es sich um einen Gas- oder Stromlastgang handelt"
    )
    version: str | None = Field(default=None, description="Versionsnummer des Lastgangs", title="Version")
    werte: list[Zeitreihenwert] | None = Field(
        default=None, description="Die im Lastgang enthaltenen Messwerte", title="Werte"
    )
    zeit_intervall_laenge: Menge | None = Field(..., alias="zeitIntervallLaenge")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
