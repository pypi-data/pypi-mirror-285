from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

from .route_section_naptan_entry_sequence import RouteSectionNaptanEntrySequence

class AffectedRoute(BaseModel):
    id: str = Field(alias='id')
    line_id: str = Field(alias='lineId')
    route_code: str = Field(alias='routeCode')
    name: str = Field(alias='name')
    line_string: str = Field(alias='lineString')
    direction: str = Field(alias='direction')
    origination_name: str = Field(alias='originationName')
    destination_name: str = Field(alias='destinationName')
    valid_to: datetime = Field(alias='validTo')
    valid_from: datetime = Field(alias='validFrom')
    route_section_naptan_entry_sequence: List[RouteSectionNaptanEntrySequence] = Field(alias='routeSectionNaptanEntrySequence')

    model_config = {'populate_by_name': True}
