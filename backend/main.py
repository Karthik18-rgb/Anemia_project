from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend import services
from .database import Base, engine, SessionLocal
from . import models, schemas, services, crud

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Anemia Risk API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()    

@app.get("/")
def home():
    return {"message": "Anemia API running"
    }

@app.post("/predict")
def predict(input_data:schemas.AnemiaInput,  db: Session = Depends(get_db)):
    result = services.run_prediction(input_data)
    saved = crud.save_record(db, input_data, result)
    return {"result": result, "record_id": saved.id}

@app.get("/patient/{patient_id}")
def get_history(patient_id: int, db: Session = Depends(get_db)):
    records = crud.get_records_by_patient(db, patient_id)
    return records