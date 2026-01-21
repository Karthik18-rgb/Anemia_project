import os
import joblib
import numpy as np
from . import schemas

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model", "anemia_model.pkl")

model = joblib.load(MODEL_PATH) 
print("Loaded model:", model)
def run_prediction(data: schemas.AnemiaInput):
    X = np.array([[data.Gender, data.Hemoglobin, data.MCH, data.MCHC, data.MCV]])
    print("Input X:", X)
    proba_array = model.predict_proba(X)
    print("predict_proba output:", proba_array)
    raw_proba = model.predict_proba(X)[0][1] * 100
    proba = 20 + 0.6 * raw_proba
    proba = max(5, min(95, proba))
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


