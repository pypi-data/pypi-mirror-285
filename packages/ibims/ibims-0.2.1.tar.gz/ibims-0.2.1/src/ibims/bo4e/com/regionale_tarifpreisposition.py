from pydantic import BaseModel, ConfigDict, Field

from ..enum.mengeneinheit import Mengeneinheit
from ..enum.preistyp import Preistyp
from ..enum.waehrungseinheit import Waehrungseinheit
from ..zusatz_attribut import ZusatzAttribut
from .regionale_preisstaffel import RegionalePreisstaffel


class RegionaleTarifpreisposition(BaseModel):
    """
    Mit dieser Komponente können Tarifpreise verschiedener Typen im Zusammenhang mit regionalen Gültigkeiten abgebildet
    werden.

    .. raw:: html

        <object data="../_static/images/bo4e/com/RegionaleTarifpreisposition.svg" type="image/svg+xml"></object>

    .. HINT::
        `RegionaleTarifpreisposition JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/RegionaleTarifpreisposition.json>`_
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
    bezugseinheit: Mengeneinheit | None = Field(
        default=None, description="Größe, auf die sich die Einheit bezieht, beispielsweise kWh, Jahr"
    )
    einheit: Waehrungseinheit | None = Field(default=None, description="Einheit des Preises (z.B. EURO)")
    mengeneinheitstaffel: Mengeneinheit | None = Field(
        default=None,
        description="Gibt an, nach welcher Menge die vorgenannte Einschränkung erfolgt (z.B. Jahresstromverbrauch in kWh)",
    )
    preisstaffeln: list[RegionalePreisstaffel] | None = Field(
        default=None,
        description="Hier sind die Staffeln mit ihren Preisangaben und regionalen Gültigkeiten definiert",
        title="Preisstaffeln",
    )
    preistyp: Preistyp | None = Field(default=None, description="Angabe des Preistypes (z.B. Grundpreis)")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
