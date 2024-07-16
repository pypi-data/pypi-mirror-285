from pydantic import BaseModel, Field
from typing import List, Optional

class LineGroup(BaseModel):
    naptan_id_reference: Optional[str] = Field(None, alias='naptanIdReference')
    station_atco_code: Optional[str] = Field(None, alias='stationActoCode')
    line_identifier: Optional[List[str]] = Field([], alias='lineIdentifier')

    model_config = {'populate_by_name': True}