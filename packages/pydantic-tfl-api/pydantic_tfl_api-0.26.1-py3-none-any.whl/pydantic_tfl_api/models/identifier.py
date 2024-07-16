from pydantic import BaseModel, Field
from typing import Optional

from .crowding import Crowding

class Identifier(BaseModel):
    id: str = Field(alias='id')
    name: str = Field(alias='name')
    uri: str = Field(alias='uri')
    full_name: Optional[str] = Field(None, alias='fullName')
    identifier_type: str = Field(alias='type')
    crowding: Optional[Crowding] = Field(None, alias='crowding')
    status: str = Field(alias='status')

    model_config = {'populate_by_name': True}