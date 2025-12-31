import pandas as pd
import joblib
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Anemia Detection App" ,layout="wide")
st.title("🩸 Anemia Detection - Phase 1 (Detection)")
st.write("This app predicts **anemia risk** using blood test values. "
         "Upload your own CSV, or use demo mode to explore.")
REQUIRED_FEATURES = ["Gender", "Hemoglobin", "MCH", "MCHC", "MCV"]

@st.cache_resource
def load_model():
    return joblib.load("model/anemia_model.pkl")

model = load_model()

@st.cache_data
def load_sample():
    return pd.read_csv("data/sample.csv")

st.sidebar.header("📂 Data Source")
use_demo = st.sidebar.checkbox("use Demo Dataset (sample.csv)",value=True)

data = None

if use_demo:
    data = load_sample()
    st.success("Demo dataset loaded (sample.csv)")
else:
    uploaded = st.sidebar.file_uploader("Upload CSV file",type=['csv'])
    if uploaded is not None:
        data = pd.read_csv(uploaded)
        st.success("Uploaded dataset loaded")
    else:
        st.warning("Upload a CSV or enable Demo mode to continue")
        st.stop()

missing = [c for c in REQUIRED_FEATURES if c not in data.columns]
if missing:
    st.error(f"Missing required columns:{missing}")
    st.stop()                

st.subheader("📊 Dataset Preview")
st.dataframe(data.head())

st.subheader("📈 Hemoglobin Distribution")
fig, ax = plt.subplots(figsize=(10,5))
sns.histplot(data["Hemoglobin"], kde=True, ax=ax)
ax.set_xlabel("Hemoglobin")
st.pyplot(fig)

st.header("🧠 Anemia Predictions")
X = data[REQUIRED_FEATURES]
preds = model.predict(X)
probs = model.predict_proba(X)[:, 1]

results = data.copy()
results["Prediction"] = preds
results["Risk Probability (%)"] = (probs * 100).round(2)

def format_results(row):
    if row["Prediction"] == 1:
        return "🟥 Anemic"
    return "🟩 Normal"

results["Status"] = results.apply(format_results, axis=1)

st.write("### 📄 Full Results table")
st.dataframe(results)

st.write("### 🔎 Inspect a specific patient")
index = st.slider("Select row", 0, len(results) - 1, 0)
selected = results.iloc[index]

st.write(selected)
st.success(f"Prediction: **{selected['Status']}**\n"
           f"Risk Probability: **{selected['Risk Probability (%)']}%**")
st.caption("Higher pribability = higher medical attention .")

st.markdown("---")
st.caption("Built by T Karthik Singh - Phase 1: Anemia Detection")
