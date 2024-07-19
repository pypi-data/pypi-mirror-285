from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ..enum.mengeneinheit import Mengeneinheit


class Zaehlpunkt(BaseModel):
    """
    The zaehlpunkt object was created during a migration project.
    It contains attributes needed for metering mapping.
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    id: str | None = Field(default=None, alias="_id", title=" Id")
    periodenverbrauch_vorhersage: Decimal = Field(
        ..., alias="periodenverbrauchVorhersage", title="Periodenverbrauchvorhersage"
    )
    einheit_vorhersage: Mengeneinheit | None = Field(default=Mengeneinheit.KWH, alias="einheitVorhersage")
    zeitreihentyp: str | None = Field(default="Z21", title="Zeitreihentyp")
    kunden_wert: Decimal | None = Field(..., alias="kundenWert", title="Kundenwert")
    einheit_kunde: Mengeneinheit | None = Field(default=None, alias="einheitKunde")
    grundzustaendiger: bool | None = Field(default=True, title="Grundzustaendiger")
