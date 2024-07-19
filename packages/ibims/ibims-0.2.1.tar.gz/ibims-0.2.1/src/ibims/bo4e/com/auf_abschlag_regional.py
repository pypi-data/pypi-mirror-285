from pydantic import BaseModel, ConfigDict, Field

from ..enum.auf_abschlagstyp import AufAbschlagstyp
from ..enum.auf_abschlagsziel import AufAbschlagsziel
from ..enum.waehrungseinheit import Waehrungseinheit
from ..zusatz_attribut import ZusatzAttribut
from .auf_abschlag_pro_ort import AufAbschlagProOrt
from .energiemix import Energiemix
from .preisgarantie import Preisgarantie
from .tarifeinschraenkung import Tarifeinschraenkung
from .vertragskonditionen import Vertragskonditionen
from .zeitraum import Zeitraum


class AufAbschlagRegional(BaseModel):
    """
    Mit dieser Komponente können Auf- und Abschläge verschiedener Typen
    im Zusammenhang mit regionalen Gültigkeiten abgebildet werden.
    Hier sind auch die Auswirkungen auf verschiedene Tarifparameter modelliert,
    die sich durch die Auswahl eines Auf- oder Abschlags ergeben.

    .. raw:: html

        <object data="../_static/images/bo4e/com/AufAbschlagRegional.svg" type="image/svg+xml"></object>

    .. HINT::
        `AufAbschlagRegional JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/AufAbschlagRegional.json>`_
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
        default=None, alias="aufAbschlagstyp", description="Typ des Aufabschlages (z.B. absolut oder prozentual)"
    )
    auf_abschlagsziel: AufAbschlagsziel | None = Field(
        default=None,
        alias="aufAbschlagsziel",
        description="Diesem Preis oder den Kosten ist der Auf/Abschlag zugeordnet. Z.B. Arbeitspreis, Gesamtpreis etc.",
    )
    beschreibung: str | None = Field(default=None, description="Beschreibung zum Auf-/Abschlag", title="Beschreibung")
    betraege: list[AufAbschlagProOrt] | None = Field(
        default=None,
        description="Werte für die gestaffelten Auf/Abschläge mit regionaler Eingrenzung",
        title="Betraege",
    )
    bezeichnung: str | None = Field(default=None, description="Bezeichnung des Auf-/Abschlags", title="Bezeichnung")
    einheit: Waehrungseinheit | None = Field(
        default=None, description="Gibt an in welcher Währungseinheit der Auf/Abschlag berechnet wird. Euro oder Ct."
    )
    einschraenkungsaenderung: Tarifeinschraenkung | None = Field(
        default=None,
        description="Änderungen in den Einschränkungen zum Tarif. Falls in dieser Komponenten angegeben,\nwerden die Tarifparameter hiermit überschrieben.",
    )
    energiemixaenderung: Energiemix | None = Field(
        default=None,
        description="Der Energiemix kann sich durch einen AufAbschlag ändern (z.B. zwei Cent Aufschlag für Ökostrom:\nSollte dies der Fall sein, wird hier die neue Zusammensetzung des Energiemix angegeben.",
    )
    garantieaenderung: Preisgarantie | None = Field(
        default=None,
        description="Änderungen in den Garantievereinbarungen. Falls in dieser Komponenten angegeben,\nwerden die Tarifparameter hiermit überschrieben.",
    )
    gueltigkeitszeitraum: Zeitraum | None = Field(
        default=None, description="Zeitraum, in dem der Abschlag zur Anwendung kommen kann"
    )
    tarifnamensaenderungen: str | None = Field(
        default=None,
        description="Durch die Anwendung des Auf/Abschlags kann eine Änderung des Tarifnamens auftreten.",
        title="Tarifnamensaenderungen",
    )
    vertagskonditionsaenderung: Vertragskonditionen | None = Field(
        default=None,
        description="Änderungen in den Vertragskonditionen. Falls in dieser Komponenten angegeben,\nwerden die Tarifparameter hiermit überschrieben.",
    )
    voraussetzungen: list[str] | None = Field(
        default=None,
        description="Voraussetzungen, die erfüllt sein müssen, damit dieser AufAbschlag zur Anwendung kommen kann",
        title="Voraussetzungen",
    )
    website: str | None = Field(
        default=None,
        description="Internetseite, auf der die Informationen zum Auf-/Abschlag veröffentlicht sind",
        title="Website",
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
    zusatzprodukte: list[str] | None = Field(
        default=None,
        description="Zusatzprodukte, die nur in Kombination mit diesem AufAbschlag erhältlich sind",
        title="Zusatzprodukte",
    )
