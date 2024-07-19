from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConcessionFee(BaseModel):
    """
    The Concession Fee object was created during a migration project.
    It contains attributes needed for metering mapping.
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    id: str | None = Field(default=None, alias="_id", title=" Id")
    market_location_id: str = Field(..., alias="marketLocationId", title="Marketlocationid")
    group: str | None = Field(default=None, title="Group")
    obis: str = Field(..., title="Obis")
    active_from: datetime = Field(..., alias="activeFrom", title="Activefrom")
    active_until: datetime | None = Field(default=None, alias="activeUntil", title="Activeuntil")
    ka: str | None = Field(default=None, title="Ka")
