from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AdditionalProperties(BaseModel):
    category: Optional[str] = Field(None, alias='category')
    key:  Optional[str] = Field(None, alias='key')
    source_system_key:  Optional[str] = Field(None, alias='sourceSystemKey')
    value:  Optional[str] = Field(None, alias='value')
    modified: Optional[datetime] = Field(None, alias='modified')

    model_config = {'populate_by_name': True}
