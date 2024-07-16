from pydantic import BaseModel, Field
from typing import Optional

class OrderedRoute(BaseModel):
    name: str = Field(alias='name')
    naptan_ids: list[str] = Field(alias='naptanIds')
    service_type: str = Field(alias='serviceType')

    model_config = {'populate_by_name': True}