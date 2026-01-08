import joblib
from pydantic import BaseModel
from datetime import date
import numpy as np
from . import schemas

model = joblib.load("model/anemia_model.pkl") 

def run_prediction(data: schemas.AnemiaInput):
    X = np.array([[data.Gender, data.Hemoglobin, data.MCH, data.MCHC, data.MCV]])
    proba = model.predict_proba(X)[0][1] * 100
    preds = int(proba >= 50)
    return{
        "probability": round(proba, 2),
        "prediction": preds,
        "gender": data.Gender,
        "hemoglobin":data.Hemoglobin,
        "mch":data.MCH,
        "mchc":data.MCHC,
        "mcv":data.MCV,
        "patient_id":data.patient_id,
        "date":data.date
    }    