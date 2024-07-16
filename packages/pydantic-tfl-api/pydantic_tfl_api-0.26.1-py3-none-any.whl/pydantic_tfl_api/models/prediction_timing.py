from pydantic import BaseModel, Field
from datetime import datetime

class PredictionTiming(BaseModel):
    countdown_server_adjustment: str = Field(alias='countdownServerAdjustment')
    source: datetime = Field(alias='source')
    insert: datetime = Field(alias='insert')
    read: datetime = Field(alias='read')
    sent: datetime = Field(alias='sent')
    received: datetime = Field(alias='received')

    model_config = {'populate_by_name': True}
