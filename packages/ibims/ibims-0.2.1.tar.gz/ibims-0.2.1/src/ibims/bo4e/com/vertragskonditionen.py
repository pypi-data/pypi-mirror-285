from pydantic import BaseModel, ConfigDict, Field

from ..zusatz_attribut import ZusatzAttribut
from .zeitraum import Zeitraum


class Vertragskonditionen(BaseModel):
    """
    Abbildung für Vertragskonditionen. Die Komponente wird sowohl im Vertrag als auch im Tarif verwendet.

    .. raw:: html

        <object data="../_static/images/bo4e/com/Vertragskonditionen.svg" type="image/svg+xml"></object>

    .. HINT::
        `Vertragskonditionen JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Vertragskonditionen.json>`_
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
    abschlagszyklus: Zeitraum | None = Field(
        default=None,
        description="In diesen Zyklen werden Abschläge gestellt. Alternativ kann auch die Anzahl in den Konditionen angeben werden.",
    )
    anzahl_abschlaege: float | None = Field(
        default=None,
        alias="anzahlAbschlaege",
        description="Anzahl der vereinbarten Abschläge pro Jahr, z.B. 12",
        title="Anzahlabschlaege",
    )
    beschreibung: str | None = Field(
        default=None,
        description='Freitext zur Beschreibung der Konditionen, z.B. "Standardkonditionen Gas"',
        title="Beschreibung",
    )
    kuendigungsfrist: Zeitraum | None = Field(
        default=None, description="Innerhalb dieser Frist kann der Vertrag gekündigt werden"
    )
    vertragslaufzeit: Zeitraum | None = Field(default=None, description="Über diesen Zeitraum läuft der Vertrag")
    vertragsverlaengerung: Zeitraum | None = Field(
        default=None,
        description="Falls der Vertrag nicht gekündigt wird, verlängert er sich automatisch um die hier angegebene Zeit",
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
