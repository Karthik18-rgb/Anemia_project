from sqlalchemy import Column, Integer, String, Float, DateTime
from backend.database import Base
from datetime import datetime

class RiskRecord(Base):
    __tablename__ = "risk_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, index=True)
    Hemoglobin = Column(Float)
    MCH = Column(Float)
    MCHC = Column(Float)
    MCV = Column(Float)
    Gender = Column(Integer)
    prediction = Column(Integer)
    probability = Column(Float)
    date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)