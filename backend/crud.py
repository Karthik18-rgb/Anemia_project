from sqlalchemy.orm import Session
from . import models, schemas

def save_record(db: Session, data: schemas.AnemiaInput, pred:  dict):
    record = models.RiskRecord(
        patient_id = data.patient_id,
        Gender = data.Gender,
        Hemoglobin = data.Hemoglobin,
        MCH = data.MCH,
        MCHC = data.MCHC,
        MCV = data.MCV,
        prediction = pred["prediction"],
        probability = pred["probability"],
        date = data.date,
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_records_by_patient(db: Session, patient_id: int):
    return(
        db.query(models.RiskRecord).filter(models.RiskRecord.patient_id==patient_id).
        order_by(models.RiskRecord.date).all()
    )