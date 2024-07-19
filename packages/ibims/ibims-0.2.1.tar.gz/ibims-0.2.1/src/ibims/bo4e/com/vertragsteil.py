from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..zusatz_attribut import ZusatzAttribut
from .menge import Menge


class Vertragsteil(BaseModel):
    """
    Abbildung für einen Vertragsteil. Der Vertragsteil wird dazu verwendet,
    eine vertragliche Leistung in Bezug zu einer Lokation (Markt- oder Messlokation) festzulegen.

    .. raw:: html

        <object data="../_static/images/bo4e/com/Vertragsteil.svg" type="image/svg+xml"></object>

    .. HINT::
        `Vertragsteil JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Vertragsteil.json>`_
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
    lokation: str | None = Field(
        default=None, description='vertraglich_fixierte_menge: Optional["Menge"] = None', title="Lokation"
    )
    maximale_abnahmemenge: Menge | None = Field(
        default=None,
        alias="maximaleAbnahmemenge",
        description="Für die Lokation festgelegte maximale Abnahmemenge (exklusiv)",
    )
    minimale_abnahmemenge: Menge | None = Field(
        default=None, alias="minimaleAbnahmemenge", description='maximale_abnahmemenge: Optional["Menge"] = None'
    )
    vertraglich_fixierte_menge: Menge | None = Field(
        default=None, alias="vertraglichFixierteMenge", description='minimale_abnahmemenge: Optional["Menge"] = None'
    )
    vertragsteilbeginn: datetime | None = Field(
        default=None,
        description="vertragsteilende: Optional[pydantic.AwareDatetime] = None",
        title="Vertragsteilbeginn",
    )
    vertragsteilende: datetime | None = Field(
        default=None, description="lokation: Optional[str] = None", title="Vertragsteilende"
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
