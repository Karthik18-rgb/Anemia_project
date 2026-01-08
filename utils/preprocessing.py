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
    data = data.copy()
    df = data.copy()
    has_date = DATE_COL in data.columns
    has_patient = PATIENT_ID in data.columns
    if has_patient:
          patient_ids = sorted(data["Patient_ID"].dropna().unique())
          selected = st.sidebar.selectbox("Select Patient", ["All"] + list(patient_ids))
          if selected != "All":
               df = data[data["Patient_ID"] == selected].copy()
          else:
              df.copy()     
    if has_date:
        df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
        df = df.sort_values(DATE_COL)
    return df, has_date, has_patient
