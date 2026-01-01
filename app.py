import pandas as pd
import joblib
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report

st.set_page_config(page_title="Anemia Detection App and Risk Monitoring" ,layout="wide")
st.title("🩸 Anemia Detection • Risk Monitoring • Recommendations")
st.write(
    "This dashboard analyzes blood test values to **detect anemia risk**, "
    "track changes over time, and provide helpful insights. "
    "Upload your own CSV — or explore using demo data."
)
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
except FileNotFoundError:
    st.error("sample.csv missing. Please upload a dataset to continue.")
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

def get_recommendation(prob, hb):
     if prob >= 80:
          return "🔴 High risk - consult a doctor soon."
     elif prob >= 50:
          return "🟠 Moderate risk - repeat test & monitor diet."
     elif hb < 11:
          return "🟡 Low hemoglobin - review iron intake."
     else:
          return "🟢 Stable - continue monitoring."    

def trend_message(hb_series):
     if len(hb_series) < 3:
          return "Insufficient visit history to analyze trend."
     change = hb_series.iloc[-1] - hb_series.iloc[-3]
     if change <= -1.0:
          return f"Hemoglobin dropped {abs(change):.1f} g/dL recently - worsening trend."
     elif change >= 1.0:
          return f"Hemoglobin improved {change:.1f} g/dL recently"
     else:
          return "Hemoglobin is relatively stable."      

def color_risk(val):
     if val >= 80:
          return "background-color:#d9534f; color:white; font-weight:bold"
     if val >= 50:
          return "background-color:#f0ad4e; color:black; font-weight:bold"
     return "background-color:#5cb85c; color:white; font-weight:bold"


st.header("🧠 Anemia Predictions")
X = df[REQUIRED_FEATURES]
preds = model.predict(X)
proba = model.predict_proba(X)[:, 1]

results = df.copy()
results["Prediction"] = preds
results["Risk Probability (%)"] = (proba * 100).round(1)
results["Recommendation"] = results.apply(lambda r: get_recommendation(r["Risk Probability (%)"], r["Hemoglobin"]), axis=1)

st.subheader("📋 Patient Risk Table")
st.dataframe(results.style.applymap(color_risk, subset=["Risk Probability (%)"]), use_container_width=True)

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
          st.error("🚨 Risk is increasing rapidly - medical review recommended.")
     elif slope > 0:
          st.warning("📈 Risk is slowly increasing - keep monitoring")
     else:
          st.success("🟢 Risk appears stable or improving")          

else:
     st.info("Add Date column to enable risk monitoring")

st.subheader("Risk Forecast (Next Visit)")
if has_date and len(results) > 2:
     results = results.sort_values(DATE_COL)
     results["Hb_Change"] = results["Hemoglobin"].diff()
     hb_trend = results["Hb_Change"].mean()
     next_hb = df["Hemoglobin"].iloc[-1] + hb_trend
     next_hb = max(next_hb, 5)

     future_row = df.iloc[-1].copy()
     future_row["Hemoglobin"] = next_hb
     future_features = future_row[REQUIRED_FEATURES].to_frame().T
     future_prob = model.predict_proba(future_features)[0, 1] * 100

     fig, ax = plt.subplots(figsize=(10,5))
     sns.lineplot(x=df[DATE_COL], y=results["Risk Probability (%)"], marker='o', label="Current Risk")
     future_date = df[DATE_COL].iloc[-1] + pd.to_timedelta(30, unit="d")
     ax.plot(future_date, future_prob, "ro--", label="Forecast (Next Visit)")
     ax.set_ylabel("Risk (%)")
     plt.xticks(rotation=30)
     fig.autofmt_xdate()
     st.pyplot(fig)

     st.subheader("🔮 Predicted Next-Visit Risk")
     st.markdown(f"""
### **{future_prob:.1f}%**
_Risk estimate based on current trend_
""")

     if future_prob >= 80:
          st.error("🔴 High likelihood of anemia worsening - medical review recommended.")
     elif future_prob >= 60:
          st.warning("🟠 Risk is gradually increasing - monitor closely")
     else:
          st.success("🟢 Risk expected to remain stable or improve")          

else:
     st.info("Need atleast 2 dated visits to forecast risk.")

if has_patient:
     st.subheader("Clinical-style Interpretation")    

st.write(trend_message(df["Hemoglobin"]))      

st.markdown("---")
st.caption("Phase 4 - Personalized Anemia Monitoring Dashboard (Educational Use Only)")             
