from pydantic import BaseModel
from typing import Optional
from datetime import date

class HarvestRequest(BaseModel):
    crop_type: str
    sowing_date: date
    location: str

class HarvestResponse(BaseModel):
    crop_type: str
    days_after_sowing: int
    maturity_percent: float
    weather_summary: str
    weather_risk_level: str
    recommendation: str
    reasoning: str
    farmer_advice: str
