from pydantic import BaseModel
from datetime import datetime, date

class AnemiaInput(BaseModel):
    patient_id: int
    Gender: int
    Hemoglobin: float
    MCH: float
    MCHC: float
    MCV: float
    date: date

class RiskRecords(BaseModel):
    id : int
    patient_id: int
    probability: int
    prediction: int
    date: datetime

    class Config:
        from_attributes = True