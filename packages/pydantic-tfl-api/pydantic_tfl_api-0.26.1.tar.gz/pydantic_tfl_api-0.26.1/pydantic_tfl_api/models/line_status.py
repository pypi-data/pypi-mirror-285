from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

from .validity_period import ValidityPeriod
from .disruption import Disruption

class LineStatus(BaseModel):
    id: int = Field(alias='id')
    line_id: Optional[str] = Field(None, alias='lineId')
    status_severity: int = Field(alias='statusSeverity')
    status_severity_description: str = Field(alias='statusSeverityDescription')
    reason: Optional[str] = Field(None, alias='reason')
    created: datetime = Field(alias='created')
    last_update: Optional[datetime] = Field(None, alias='lastUpdate')
    validity_periods: List[ValidityPeriod] = Field(None, alias='validityPeriods')
    disruptions: Optional[List[Disruption]] = Field([], alias='disruptions')

    model_config = {'populate_by_name': True}