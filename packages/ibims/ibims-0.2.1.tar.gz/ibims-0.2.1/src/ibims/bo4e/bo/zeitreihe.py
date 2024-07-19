from pydantic import BaseModel, ConfigDict, Field

from ..com.zeitreihenwert import Zeitreihenwert
from ..enum.medium import Medium
from ..enum.mengeneinheit import Mengeneinheit
from ..enum.messart import Messart
from ..enum.messgroesse import Messgroesse
from ..enum.typ import Typ
from ..enum.wertermittlungsverfahren import Wertermittlungsverfahren
from ..zusatz_attribut import ZusatzAttribut


class Zeitreihe(BaseModel):
    """
    Abbildung einer allgemeinen Zeitreihe mit einem Wertvektor.
    Die Werte können mit wahlfreier zeitlicher Distanz im Vektor abgelegt sein.

    .. raw:: html

        <object data="../_static/images/bo4e/bo/Zeitreihe.svg" type="image/svg+xml"></object>

    .. HINT::
        `Zeitreihe JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/bo/Zeitreihe.json>`_
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
    typ: Typ = Field(..., alias="_typ", description="Bezeichnung für die Zeitreihe")
    beschreibung: str | None = Field(
        default=None, description="Beschreibt die Verwendung der Zeitreihe", title="Beschreibung"
    )
    bezeichnung: str | None = Field(default=None, description="Bezeichnung für die Zeitreihe", title="Bezeichnung")
    einheit: Mengeneinheit | None = Field(
        default=None, description="Alle Werte in der Tabelle haben die Einheit, die hier angegeben ist"
    )
    medium: Medium | None = Field(
        default=None, description="Medium, das gemessen wurde (z.B. Wasser, Dampf, Strom, Gas)"
    )
    messart: Messart | None = Field(
        default=None, description="Beschreibt die Art der Messung (z.B. aktueller Wert, mittlerer Wert, maximaler Wert)"
    )
    messgroesse: Messgroesse | None = Field(
        default=None, description="Beschreibt, was gemessen wurde (z.B. Strom, Spannung, Wirkleistung, Scheinleistung)"
    )
    version: str | None = Field(default=None, description="Version der Zeitreihe", title="Version")
    werte: list[Zeitreihenwert] | None = Field(default=None, description="Hier liegen jeweils die Werte", title="Werte")
    wertherkunft: Wertermittlungsverfahren | None = Field(
        default=None, description="Kennzeichnung, wie die Werte entstanden sind, z.B. durch Messung"
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
