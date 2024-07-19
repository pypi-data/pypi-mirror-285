from pydantic import BaseModel, ConfigDict, Field

from ..enum.messwertstatus import Messwertstatus
from ..enum.messwertstatuszusatz import Messwertstatuszusatz
from ..zusatz_attribut import ZusatzAttribut
from .zeitspanne import Zeitspanne


class Zeitreihenwert(BaseModel):
    """
    Abbildung eines Zeitreihenwertes bestehend aus Zeitraum, Wert und Statusinformationen.

    .. raw:: html

        <object data="../_static/images/bo4e/com/Zeitreihenwert.svg" type="image/svg+xml"></object>

    .. HINT::
        `Zeitreihenwert JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Zeitreihenwert.json>`_
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
    status: Messwertstatus | None = Field(
        default=None, description="Der Status gibt an, wie der Wert zu interpretieren ist, z.B. in Berechnungen."
    )
    statuszusatz: Messwertstatuszusatz | None = Field(
        default=None,
        description="Eine Zusatzinformation zum Status, beispielsweise ein Grund für einen fehlenden Wert.",
    )
    wert: float | None = Field(default=None, description="Zeitespanne für das Messintervall", title="Wert")
    zeitspanne: Zeitspanne | None = Field(default=None, description="Zeitespanne für das Messintervall")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
