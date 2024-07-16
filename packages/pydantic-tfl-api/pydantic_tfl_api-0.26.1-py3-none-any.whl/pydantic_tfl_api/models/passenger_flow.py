from pydantic import BaseModel, Field
from typing import Optional

class PassengerFlow(BaseModel):
    time_slice: Optional[str] = Field(None, alias='timeSlice')
    value: Optional[int] = Field(None, alias='value')

    model_config = {'populate_by_name': True}