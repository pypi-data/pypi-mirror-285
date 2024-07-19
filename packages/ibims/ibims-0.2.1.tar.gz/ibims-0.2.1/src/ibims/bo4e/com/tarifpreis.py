from pydantic import BaseModel, ConfigDict, Field

from ..enum.mengeneinheit import Mengeneinheit
from ..enum.preisstatus import Preisstatus
from ..enum.preistyp import Preistyp
from ..enum.waehrungseinheit import Waehrungseinheit
from ..zusatz_attribut import ZusatzAttribut


class Tarifpreis(BaseModel):
    """
    Abbildung eines Tarifpreises mit Preistyp und Beschreibung abgeleitet von COM Preis.

    .. raw:: html

        <object data="../_static/images/bo4e/com/Tarifpreis.svg" type="image/svg+xml"></object>

    .. HINT::
        `Tarifpreis JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/com/Tarifpreis.json>`_
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
    beschreibung: str | None = Field(
        default=None,
        description='Beschreibung des Preises. Hier können z.B. Preisdetails angegeben sein, beispielsweise "Drehstromzähler".',
        title="Beschreibung",
    )
    bezugswert: Mengeneinheit | None = Field(
        default=None, description="Angabe, für welche Bezugsgröße der Preis gilt. Z.B. kWh."
    )
    einheit: Waehrungseinheit | None = Field(
        default=None, description="Währungseinheit für den Preis, z.B. Euro oder Ct."
    )
    preistyp: Preistyp | None = Field(default=None, description="Angabe des Preistypes (z.B. Grundpreis)")
    status: Preisstatus | None = Field(default=None, description="Gibt den Status des veröffentlichten Preises an")
    wert: float | None = Field(default=None, description="Gibt die nominale Höhe des Preises an.", title="Wert")
    zusatz_attribute: list[ZusatzAttribut] | None = Field(
        default=None, alias="zusatzAttribute", title="Zusatzattribute"
    )
