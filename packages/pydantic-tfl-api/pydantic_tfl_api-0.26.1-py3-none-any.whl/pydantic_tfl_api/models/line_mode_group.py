from pydantic import BaseModel, Field
from typing import List

class LineModeGroup(BaseModel):
    mode_name: str = Field(alias='modeName')
    line_identifier: List[str] = Field(alias='lineIdentifier')

    model_config = {'populate_by_name': True}