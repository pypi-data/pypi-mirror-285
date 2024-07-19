from pydantic import BaseModel, ConfigDict, Field

from ..enum.auf_abschlagstyp import AufAbschlagstyp
from ..enum.auf_abschlagsziel import AufAbschlagsziel
from ..enum.waehrungseinheit import Waehrungseinheit
from ..zusatz_attribut import ZusatzAttribut
from .preisstaffel import Preisstaffel
from .zeitraum import Zeitraum


class AufAbschlag(BaseModel):
    """
    Modell für die preiserhöhenden (Aufschlag) bzw. preisvermindernden (Abschlag) Zusatzvereinbarungen,
    die individuell zu einem neuen oder bestehenden Liefervertrag abgeschlossen wurden.

    .. raw:: html

        <object data="../_static/images/bo4e/com/AufAbschlag.svg" type="image/svg+xml"></object>

    .. HINT::
        `AufAbschlag JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/AufAbschlag.json>`_
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
        default=None, alias="aufAbschlagstyp", description="Typ des Aufabschlages (z.B. absolut oder prozentual)."
    )
    auf_abschlagsziel: AufAbschlagsziel | None = Field(
        default=None,
        alias="aufAbschlagsziel",
        description="Diesem Preis oder den Kosten ist der Auf/Abschlag zugeordnet. Z.B. Arbeitspreis, Gesamtpreis etc..",
    )
    beschreibung: str | None = Field(default=None, description="Beschreibung zum Auf-/Abschlag", title="Beschreibung")
    bezeichnung: str | None = Field(default=None, description="Bezeichnung des Auf-/Abschlags", title="Bezeichnung")
    einheit: Waehrungseinheit | None = Field(
        default=None, description="Internetseite, auf der die Informationen zum Auf-/Abschlag veröffentlicht sind."
    )
    gueltigkeitszeitraum: Zeitraum | None = Field(
        default=None, description="Internetseite, auf der die Informationen zum Auf-/Abschlag veröffentlicht sind."
    )
    staffeln: list[Preisstaffel] | None = Field(
        default=None, description="Werte für die gestaffelten Auf/Abschläge.", title="Staffeln"
    )
    website: str | None = Field(
        default=None,
        description="Internetseite, auf der die Informationen zum Auf-/Abschlag veröffentlicht sind.",
        title="Website",
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
