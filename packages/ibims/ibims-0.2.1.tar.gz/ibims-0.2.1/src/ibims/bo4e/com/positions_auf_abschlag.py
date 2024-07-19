from pydantic import BaseModel, ConfigDict, Field

from ..enum.auf_abschlagstyp import AufAbschlagstyp
from ..enum.waehrungseinheit import Waehrungseinheit
from ..zusatz_attribut import ZusatzAttribut


class PositionsAufAbschlag(BaseModel):
    """
    Differenzierung der zu betrachtenden Produkte anhand der preiserhöhenden (Aufschlag)
    bzw. preisvermindernden (Abschlag) Zusatzvereinbarungen,
    die individuell zu einem neuen oder bestehenden Liefervertrag abgeschlossen werden können.
    Es können mehrere Auf-/Abschläge gleichzeitig ausgewählt werden.

    .. raw:: html

        <object data="../_static/images/bo4e/com/PositionsAufAbschlag.svg" type="image/svg+xml"></object>

    .. HINT::
        `PositionsAufAbschlag JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/PositionsAufAbschlag.json>`_
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
    auf_abschlagstyp: AufAbschlagstyp | None = Field(
        default=None, alias="aufAbschlagstyp", description="Typ des AufAbschlages"
    )
    auf_abschlagswaehrung: Waehrungseinheit | None = Field(
        default=None,
        alias="aufAbschlagswaehrung",
        description="Einheit, in der der Auf-/Abschlag angegeben ist (z.B. ct/kWh).",
    )
    auf_abschlagswert: float | None = Field(
        default=None, alias="aufAbschlagswert", description="Höhe des Auf-/Abschlages", title="Aufabschlagswert"
    )
    beschreibung: str | None = Field(default=None, description="Beschreibung zum Auf-/Abschlag", title="Beschreibung")
    bezeichnung: str | None = Field(default=None, description="Bezeichnung des Auf-/Abschlags", title="Bezeichnung")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
