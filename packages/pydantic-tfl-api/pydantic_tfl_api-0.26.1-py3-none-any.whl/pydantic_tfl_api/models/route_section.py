from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class RouteSection(BaseModel):
    route_code: Optional[str] = Field(None, alias='routeCode')
    name: str = Field(alias='name')
    direction: Optional[str] = Field(None, alias='direction')
    origination_name: str = Field(alias='originationName')
    destination_name: str = Field(alias='destinationName')
    originator: str = Field(alias='originator')
    destination: str = Field(alias='destination')
    service_type: Optional[str] = Field(None, alias='serviceType')
    valid_to: Optional[datetime] = Field(None, alias='validTo')
    valid_from: Optional[datetime] = Field(None, alias='validFrom')

    model_config = {'populate_by_name': True}
