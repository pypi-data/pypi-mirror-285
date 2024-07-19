from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ..enum.ablesende_rolle import AblesendeRolle
from ..enum.ablesungsstatus import Ablesungsstatus
from ..enum.mengeneinheit import Mengeneinheit
from ..enum.messwertstatus import Messwertstatus
from ..enum.wertermittlungsverfahren import Wertermittlungsverfahren
from ..zusatz_attribut import ZusatzAttribut


class Verbrauch(BaseModel):
    """
    Abbildung eines zeitlich abgegrenzten Verbrauchs

    .. raw:: html

        <object data="../_static/images/bo4e/com/Verbrauch.svg" type="image/svg+xml"></object>

    .. HINT::
        `Verbrauch JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Verbrauch.json>`_
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
    einheit: Mengeneinheit | None = Field(default=None, description="Gibt die Einheit zum jeweiligen Wert an")
    enddatum: datetime | None = Field(
        default=None,
        description="Exklusives Ende des Zeitraumes, für den der Verbrauch angegeben wird",
        title="Enddatum",
    )
    messwertstatus: Messwertstatus | None = None
    obis_kennzahl: str = Field(
        ...,
        alias="obisKennzahl",
        description="Die OBIS-Kennzahl für den Wert, die festlegt, welche Größe mit dem Stand gemeldet wird, z.B. '1-0:",
        title="Obiskennzahl",
    )
    startdatum: datetime | None = Field(
        default=None,
        description="Inklusiver Beginn des Zeitraumes, für den der Verbrauch angegeben wird",
        title="Startdatum",
    )
    wert: float = Field(..., description="Gibt den absoluten Wert der Menge an", title="Wert")
    wertermittlungsverfahren: Wertermittlungsverfahren | None = Field(
        default=None, description="Gibt an, ob es sich um eine PROGNOSE oder eine MESSUNG handelt"
    )
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
    ablesegrund: str | None = Field(default=None, title="Ablesegrund")
    ablesebeschreibung: str | None = Field(default=None, title="Ablesebeschreibung")
    periodenverbrauch: Decimal | None = Field(default=None, title="Periodenverbrauch")
    periodenverbrauch_ursprung: str | None = Field(
        default=None, alias="periodenverbrauchUrsprung", title="Periodenverbrauchursprung"
    )
    ableser: AblesendeRolle | None = None
    status: Ablesungsstatus | None = None
    energiegehalt_gas: Decimal | None = Field(default=None, alias="energiegehaltGas", title="Energiegehaltgas")
    energiegehalt_gas_gueltig_von: datetime | None = Field(
        default=None, alias="energiegehaltGasGueltigVon", title="Energiegehaltgasgueltigvon"
    )
    energiegehalt_gas_gueltig_bis: datetime | None = Field(
        default=None, alias="energiegehaltGasGueltigBis", title="Energiegehaltgasgueltigbis"
    )
    umwandlungsfaktor_gas: Decimal | None = Field(
        default=None, alias="umwandlungsfaktorGas", title="Umwandlungsfaktorgas"
    )
    umwandlungsfaktor_gas_gueltig_von: datetime | None = Field(
        default=None, alias="umwandlungsfaktorGasGueltigVon", title="Umwandlungsfaktorgasgueltigvon"
    )
    umwandlungsfaktor_gas_gueltig_bis: datetime | None = Field(
        default=None, alias="umwandlungsfaktorGasGueltigBis", title="Umwandlungsfaktorgasgueltigbis"
    )
