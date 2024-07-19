from pydantic import BaseModel, ConfigDict, Field

from ..zusatz_attribut import ZusatzAttribut
from .regionale_gueltigkeit import RegionaleGueltigkeit
from .sigmoidparameter import Sigmoidparameter


class RegionalePreisstaffel(BaseModel):
    """
    Abbildung einer Preisstaffel mit regionaler Abgrenzung

    .. raw:: html

        <object data="../_static/images/bo4e/com/RegionalePreisstaffel.svg" type="image/svg+xml"></object>

    .. HINT::
        `RegionalePreisstaffel JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/RegionalePreisstaffel.json>`_
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
    einheitspreis: float | None = Field(
        default=None, description="Preis pro abgerechneter Mengeneinheit", title="Einheitspreis"
    )
    regionale_gueltigkeit: RegionaleGueltigkeit | None = Field(
        default=None, alias="regionaleGueltigkeit", description="Regionale Eingrenzung der Preisstaffel"
    )
    sigmoidparameter: Sigmoidparameter | None = Field(
        default=None,
        description="Parameter zur Berechnung des Preises anhand der Jahresmenge und weiterer netzbezogener Parameter",
    )
    staffelgrenze_bis: float | None = Field(
        default=None,
        alias="staffelgrenzeBis",
        description="Exklusiver oberer Wert, bis zu dem die Staffel gilt",
        title="Staffelgrenzebis",
    )
    staffelgrenze_von: float | None = Field(
        default=None,
        alias="staffelgrenzeVon",
        description="Inklusiver unterer Wert, ab dem die Staffel gilt",
        title="Staffelgrenzevon",
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
