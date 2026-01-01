import pandas as pd
import joblib
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report

st.set_page_config(page_title="Anemia Detection App and Risk Monitoring" ,layout="wide")
st.title("🩸 Anemia Detection & Risk Monitoring - Phase 2")
st.write("This app predicts **anemia risk** using blood test values. "
         "Upload your own CSV, or use demo mode to explore.")
REQUIRED_FEATURES = ["Gender", "Hemoglobin", "MCH", "MCHC", "MCV"]
DATE_COL = "Date"
PATIENT_ID = "Patient_ID"

@st.cache_resource
def load_model():
    return joblib.load("model/anemia_model.pkl")

model = load_model()

@st.cache_data
def load_data(path):
    return pd.read_csv(path)

try: 
    data = load_data("data/sample.csv")
    st.info("Demo dataset loaded. Upload your own CSV to analyze real data")
except:
    st.error("sample.csv missing.")
    st.stop()

uploaded = st.sidebar.file_uploader("Upload CSV file",type=['csv'])
if uploaded is not None:
        data = pd.read_csv(uploaded)
        st.success("File uploaded!")

missing = [c for c in REQUIRED_FEATURES if c not in data.columns]
if missing:
    st.error(f"Missing required columns:{missing}")
    st.stop()   


has_date = DATE_COL in data.columns
if has_date:
     data[DATE_COL]=pd.to_datetime(data[DATE_COL], errors='coerce')
     data = data.sort_values(DATE_COL)  


has_patient = PATIENT_ID in data.columns
if has_patient:
     patient_ids = sorted(data[PATIENT_ID].unique())
     selected = st.selectbox("Select Patient", patient_ids)
     df = data[data[PATIENT_ID] == selected]
else:
     df = data


st.header("🧠 Anemia Predictions")
X = df[REQUIRED_FEATURES]
preds = model.predict(X)
proba = model.predict_proba(X)[:, 1]

results = df.copy()
results["Prediction"] = preds
results["Risk Probability (%)"] = (proba * 100).round(1)

st.write("Patient Records")
st.dataframe(results)

st.subheader("📈 Hemoglobin Distribution")
fig, ax = plt.subplots(figsize=(10,5))
sns.histplot(data["Hemoglobin"], kde=True, ax=ax)
ax.set_xlabel("Hemoglobin")
st.pyplot(fig)

st.subheader("Hemoglobin Trend")
if has_date:
     fig, ax = plt.subplots(figsize=(10,5))
     sns.lineplot(x=df[DATE_COL], y=df["Hemoglobin"], marker='o',ax=ax)
     ax.axhline(12,label="Low Threshold", color="red", linestyle="--")
     ax.set_ylabel("Hemoglobin")
     ax.legend()
     plt.xticks(rotation=30)
     fig.autofmt_xdate()
     st.pyplot(fig)
else:
     st.info("Add Date column to see trends.")    

st.subheader("Risk Trend")
if has_date:
     fig, ax = plt.subplots(figsize=(10,5))
     sns.lineplot(x=df[DATE_COL], y=results["Risk Probability (%)"], marker='o', ax=ax)
     ax.set_ylabel("Risk (%)")
     plt.xticks(rotation=30)
     fig.autofmt_xdate()
     st.pyplot(fig)

     slope = results["Risk Probability (%)"].diff().mean()
     if slope > 5:
          st.error("Risk is increasing rapidly - medical review recommended.")
     elif slope > 0:
          st.warning("Risk is slowly increasing - keep monitoring")
     else:
          st.success("Risk appears stable or improving")          

else:
     st.info("Add Date column to enable risk monitoring")

st.markdown("---")
st.caption("Phase 2 - Anemia Monitoring Dashboard")             
