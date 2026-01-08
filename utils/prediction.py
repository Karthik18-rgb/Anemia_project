import pandas as pd
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/predict"
REQUIRED_FEATURES = ["Gender", "Hemoglobin", "MCH", "MCHC", "MCV"]

def run_predictions(df:pd.DataFrame, model, features):

    missing = [c for c in REQUIRED_FEATURES if c not in df.columns]
    if missing:
        st.error(f"Missing required columns:{missing}")
        st.stop()

    results = df.copy()

    proba = []
    

    for _,row in df.iterrows():

        payload = {
            "patient_id": int(row.get("Patient_ID", 0)),
            "date" : str(row.get("Date", "")),
            "Gender" : int(row["Gender"]),
            "Hemoglobin" : float(row["Hemoglobin"]),
            "MCH" : float(row["MCH"]),
            "MCHC" : float(row["MCHC"]),
            "MCV" : float(row["MCV"]),
        }

        try:
            r = requests.post(API_URL, json=payload)
            if r.status_code == 200:
                data = r.json()
                prob = data.get("result",{}).get("probability", None)
                proba.append(prob)
            else:
                st.error(f"Backend error {r.status_code}:{r.text}")
                proba.append(None)


        except Exception as e:
            st.error(f"Backend error: {e}")
            proba.append(None)
            
    results["Risk Probability (%)"] = proba
    results["Prediction"] = results["Risk Probability (%)"].apply(lambda x : 1 if x is not None and x >= 50 else 0)

    return results

def forecast_next_visit(results, df, model):
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        results["Date"] = pd.to_datetime(results["Date"], errors="coerce")

    results = results.sort_values("Date")
    results["Hb_Change"] = results["Hemoglobin"].diff()
    hb_trend = results["Hb_Change"].mean()
    next_hb = df["Hemoglobin"].iloc[-1] + hb_trend
    next_hb = max(next_hb, 5)

    future_row = df.iloc[-1].copy()
    future_row["Hemoglobin"] = next_hb
    future_features = future_row[REQUIRED_FEATURES].to_frame().T
    future_prob = model.predict_proba(future_features)[0, 1] * 100
    future_date = df["Date"].iloc[-1] + pd.to_timedelta(30, unit="d")

    return future_prob, future_date