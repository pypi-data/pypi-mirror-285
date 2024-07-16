from pydantic import BaseModel, Field

from .stop_point import StopPoint

class RouteSectionNaptanEntrySequence(BaseModel):
    ordinal: int = Field(alias='ordinal')
    stop_point: StopPoint = Field(alias='stopPoint')

    model_config = {'populate_by_name': True}
