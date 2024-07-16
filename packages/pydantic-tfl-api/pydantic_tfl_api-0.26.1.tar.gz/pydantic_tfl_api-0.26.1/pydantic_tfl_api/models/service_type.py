from pydantic import BaseModel, Field

class ServiceType(BaseModel):
    name: str = Field(alias='name')
    uri: str = Field(alias='uri')

    model_config = {'populate_by_name': True}
