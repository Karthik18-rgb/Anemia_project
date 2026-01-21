import pandas as pd
import requests
import streamlit as st
import time

session = requests.Session()

API_URL = "https://anemiaproject-production.up.railway.app/predict"
REQUIRED_FEATURES = ["Gender", "Hemoglobin", "MCH", "MCHC", "MCV"]

def run_predictions(df:pd.DataFrame, model, features):
    df["Patient_ID"] = pd.to_numeric(df["Patient_ID"], errors='coerce').astype("Int64")
    if pd.api.types.is_datetime64_any_dtype(df["Patient_ID"]):
        st.error('BUG')
        st.stop()

    missing = [c for c in REQUIRED_FEATURES if c not in df.columns]
    if missing:
        st.error(f"Missing required columns:{missing}")
        st.stop()

    df = df.sort_values(by=["Patient_ID", "Date"],key=lambda col: col.astype("Int64") if col.name == "Patient_ID" else col).copy()
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
            time.sleep(1.5)
            r = session.post(API_URL, json=payload, timeout=60, headers={"Content-Type": "application/json"})
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
    results["Risk Probability (%)"] = (results["Risk Probability (%)"].rolling(window=3, min_periods=1).mean())
    results["Prediction"] = results["Risk Probability (%)"].apply(lambda x : 1 if x is not None and x >= 50 else 0)

    return results

def forecast_next_visit(results, df, model):
    df = df.copy()
    results=results.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    results["Date"] = pd.to_datetime(results["Date"], errors="coerce")

    if len(results) < 3:
        return None, None
    df = df.sort_values("Date")
    results = results.sort_values("Date")
    current_prob = float(results["Risk Probability (%)"].iloc[-1])
    recent_hb = df["Hemoglobin"].tail(3)
    hb_trend = recent_hb.diff().mean()
    trend_impact = -hb_trend * 8.0
    future_prob = current_prob + trend_impact
    future_prob = max(5.0, min(95.0, future_prob))
    future_date = df["Date"].iloc[-1] + pd.to_timedelta(30, unit="d")

    return round(float(future_prob), 2), future_date