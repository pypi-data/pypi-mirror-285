from pydantic import BaseModel, ConfigDict, Field

from ..enum.oekolabel import Oekolabel
from ..enum.oekozertifikat import Oekozertifikat
from ..enum.sparte import Sparte
from ..zusatz_attribut import ZusatzAttribut
from .energieherkunft import Energieherkunft


class Energiemix(BaseModel):
    """
    Zusammensetzung der gelieferten Energie aus den verschiedenen Primärenergieformen.

    .. raw:: html

        <object data="../_static/images/bo4e/com/Energiemix.svg" type="image/svg+xml"></object>

    .. HINT::
        `Energiemix JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Energiemix.json>`_
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
    anteil: list[Energieherkunft] | None = Field(
        default=None, description="Anteile der jeweiligen Erzeugungsart", title="Anteil"
    )
    atommuell: float | None = Field(
        default=None, description="Höhe des erzeugten Atommülls in g/kWh", title="Atommuell"
    )
    bemerkung: str | None = Field(default=None, description="Bemerkung zum Energiemix", title="Bemerkung")
    bezeichnung: str | None = Field(default=None, description="Bezeichnung des Energiemix", title="Bezeichnung")
    co2_emission: float | None = Field(
        default=None, alias="co2Emission", description="Höhe des erzeugten CO2-Ausstosses in g/kWh", title="Co2Emission"
    )
    energieart: Sparte | None = Field(default=None, description="Strom oder Gas etc.")
    energiemixnummer: int | None = Field(
        default=None, description="Eindeutige Nummer zur Identifizierung des Energiemixes", title="Energiemixnummer"
    )
    gueltigkeitsjahr: int | None = Field(
        default=None, description="Jahr, für das der Energiemix gilt", title="Gueltigkeitsjahr"
    )
    ist_in_oeko_top_ten: bool | None = Field(
        default=None,
        alias="istInOekoTopTen",
        description="Kennzeichen, ob der Versorger zu den Öko Top Ten gehört",
        title="Istinoekotopten",
    )
    oekolabel: list[Oekolabel] | None = Field(
        default=None, description="Ökolabel für den Energiemix", title="Oekolabel"
    )
    oekozertifikate: list[Oekozertifikat] | None = Field(
        default=None, description="Zertifikate für den Energiemix", title="Oekozertifikate"
    )
    website: str | None = Field(
        default=None, description="Internetseite, auf der die Strommixdaten veröffentlicht sind", title="Website"
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
