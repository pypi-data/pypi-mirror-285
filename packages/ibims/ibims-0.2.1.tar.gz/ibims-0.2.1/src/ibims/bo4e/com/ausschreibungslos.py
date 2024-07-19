from pydantic import BaseModel, ConfigDict, Field

from ..enum.preismodell import Preismodell
from ..enum.rechnungslegung import Rechnungslegung
from ..enum.sparte import Sparte
from ..enum.vertragsform import Vertragsform
from ..zusatz_attribut import ZusatzAttribut
from .ausschreibungsdetail import Ausschreibungsdetail
from .menge import Menge
from .zeitraum import Zeitraum


class Ausschreibungslos(BaseModel):
    """
    Eine Komponente zur Abbildung einzelner Lose einer Ausschreibung

    .. raw:: html

        <object data="../_static/images/bo4e/com/Ausschreibungslos.svg" type="image/svg+xml"></object>

    .. HINT::
        `Ausschreibungslos JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Ausschreibungslos.json>`_
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
    anzahl_lieferstellen: int | None = Field(
        default=None,
        alias="anzahlLieferstellen",
        description="Anzahl der Lieferstellen in dieser Ausschreibung",
        title="Anzahllieferstellen",
    )
    bemerkung: str | None = Field(default=None, description="Bemerkung des Kunden zum Los", title="Bemerkung")
    betreut_durch: str | None = Field(
        default=None, alias="betreutDurch", description="Name des Lizenzpartners", title="Betreutdurch"
    )
    bezeichnung: str | None = Field(default=None, description="Bezeichnung der Ausschreibung", title="Bezeichnung")
    energieart: Sparte | None = Field(default=None, description="Unterscheidungsmöglichkeiten für die Sparte")
    gesamt_menge: Menge | None = Field(
        default=None,
        alias="gesamtMenge",
        description="Gibt den Gesamtjahresverbrauch (z.B. in kWh) aller in diesem Los enthaltenen Lieferstellen an",
    )
    lieferstellen: list[Ausschreibungsdetail] | None = Field(
        default=None, description="Die ausgeschriebenen Lieferstellen", title="Lieferstellen"
    )
    lieferzeitraum: Zeitraum | None = Field(
        default=None,
        description="Zeitraum, für den die in diesem Los enthaltenen Lieferstellen beliefert werden sollen",
    )
    losnummer: str | None = Field(default=None, description="Laufende Nummer des Loses", title="Losnummer")
    preismodell: Preismodell | None = Field(
        default=None, description="Bezeichnung der Preismodelle in Ausschreibungen für die Energielieferung"
    )
    wiederholungsintervall: Zeitraum | None = Field(
        default=None, description="Kundenwunsch zur Kündigungsfrist in der Ausschreibung"
    )
    wunsch_kuendingungsfrist: Zeitraum | None = Field(
        default=None,
        alias="wunschKuendingungsfrist",
        description="Kundenwunsch zur Kündigungsfrist in der Ausschreibung",
    )
    wunsch_maximalmenge: Menge | None = Field(
        default=None, alias="wunschMaximalmenge", description="Maximalmenge Toleranzband (kWh, %)"
    )
    wunsch_mindestmenge: Menge | None = Field(
        default=None, alias="wunschMindestmenge", description="Mindesmenge Toleranzband (kWh, %)"
    )
    wunsch_rechnungslegung: Rechnungslegung | None = Field(
        default=None,
        alias="wunschRechnungslegung",
        description="Aufzählung der Möglichkeiten zur Rechnungslegung in Ausschreibungen",
    )
    wunsch_vertragsform: Vertragsform | None = Field(
        default=None,
        alias="wunschVertragsform",
        description="Aufzählung der Möglichkeiten zu Vertragsformen in Ausschreibungen",
    )
    wunsch_zahlungsziel: Zeitraum | None = Field(
        default=None, alias="wunschZahlungsziel", description="Kundenwunsch zum Zahlungsziel in der Ausschreibung"
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
