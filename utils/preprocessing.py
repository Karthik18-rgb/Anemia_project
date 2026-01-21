import pandas as pd
import streamlit as st

DATE_COL = "Date"
PATIENT_ID = "Patient_ID"

def load_data(path):
    try: 
        return pd.read_csv(path)
    except Exception:
        st.warning("No default dataset found. Using empty dataset until upload.")
        return pd.DataFrame()


def prepare_patient_view(data:pd.DataFrame):
    df = data.copy()
    has_date = DATE_COL in data.columns
    has_patient = PATIENT_ID in data.columns
    selected_patient = "All"
    if has_patient:
          df[PATIENT_ID] = pd.to_numeric(df[PATIENT_ID], errors='coerce').astype("Int64")
          patient_ids = sorted(df[PATIENT_ID].dropna().unique().tolist())
          if len(patient_ids) > 0:
              selected_patient = st.sidebar.selectbox("Select Patient",["All"]+patient_ids,index=0,key="selected_patient")
          if selected_patient != "All":
              df=df[df[PATIENT_ID] == selected_patient].copy()
    if has_date:
        df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
        df = df.sort_values(by=DATE_COL)
        
    if PATIENT_ID in df.columns and pd.api.types.is_datetime64_any_dtype(df[PATIENT_ID]):
        df[PATIENT_ID] = df[PATIENT_ID].astype("Int64")    
    return df, has_date, has_patient
