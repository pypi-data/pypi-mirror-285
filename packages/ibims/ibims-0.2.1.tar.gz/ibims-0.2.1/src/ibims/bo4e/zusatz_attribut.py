from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ZusatzAttribut(BaseModel):
    """
    Viele Datenobjekte weisen in unterschiedlichen Systemen eine eindeutige ID (Kundennummer, GP-Nummer etc.) auf.
    Beim Austausch von Datenobjekten zwischen verschiedenen Systemen ist es daher hilfreich,
    sich die eindeutigen IDs der anzubindenden Systeme zu merken.

    .. raw:: html

        <object data="../_static/images/bo4e/com/ZusatzAttribut.svg" type="image/svg+xml"></object>

    .. HINT::
        `ZusatzAttribut JSON Schema <https://json-schema.app/view/%23?url=https://raw.githubusercontent.com/BO4E/BO4E-Schemas/v202401.2.1/src/bo4e_schemas/ZusatzAttribut.json>`_
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )
    name: str | None = Field(
        ...,
        description='Bezeichnung der externen Referenz (z.B. "microservice xyz" oder "SAP CRM GP-Nummer")',
        title="Name",
    )
    wert: Any = Field(
        ...,
        description='Bezeichnung der externen Referenz (z.B. "microservice xyz" oder "SAP CRM GP-Nummer")',
        title="Wert",
    )
