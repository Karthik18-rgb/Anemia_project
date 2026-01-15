import pandas as pd
import joblib
import streamlit as st
import os
import tempfile

from datetime import datetime
from utils.preprocessing import load_data, prepare_patient_view
from utils.prediction import run_predictions, forecast_next_visit
from utils.risk import get_recommendation, trend_message, color_risk
from utils.plot import plot_hb_dist, plot_hb_trend, plot_risk_trend, plot_forecast
from utils.pdf_export import generate_pdf

st.set_page_config(page_title="Anemia Detection App and Risk Monitoring" ,layout="wide")
st.title("🩸 Anemia Detection • Risk Monitoring • Recommendations")
st.write(
    "This dashboard analyzes blood test values to **detect anemia risk**, "
    "track changes over time, and provide helpful insights. "
)

st.sidebar.subheader("🔐 Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
if username != "doctor" or password != "anemia123":
     st.warning("Please login to continue")
     st.stop()

st.sidebar.markdown("---")
st.sidebar.subheader("📂 Data input Method")
mode = st.sidebar.radio("Choose data input method", ["Demo mode", "Upload CSV", "Manual Entry"])

REQUIRED_FEATURES = ["Gender", "Hemoglobin", "MCH", "MCHC", "MCV"]
data = None

if mode == "Demo mode":
     try: 
          data = load_data("data/sample.csv")
          st.info("🧪 Demo dataset loaded. Upload your own CSV to analyze real data")
     except FileNotFoundError:
          st.error("sample.csv missing.")
          st.stop()

elif mode == "Upload CSV":
     uploaded = st.sidebar.file_uploader("Upload CSV file",type=['csv'])
     if uploaded:
        data = pd.read_csv(uploaded)
        st.success("File uploaded!")  
     else:
          st.warning("Upload a CSV to continue.")
          st.stop()    

elif mode == "Manual Entry":
     st.subheader("📝 Enter Patient Data")
     if "manual_data" not in st.session_state:
          st.session_state.manual_data = pd.DataFrame(columns=["Patient_ID", "Date", "Gender", "Hemoglobin", "MCH", "MCHC", "MCV"])
     pid = st.number_input("Patient ID", step=1, min_value=0)
     visit_date = st.date_input("Visit Date")
     gender = st.selectbox("Gender (0 = Female, 1 = Male)", [0, 1])
     hb = st.number_input("Hemoglobin", format="%.1f")
     mch = st.number_input("MCH", format="%.1f")
     mchc = st.number_input("MCHC", format="%.1f")
     mcv = st.number_input("MCV", format="%.1f")

     if st.button("Add Visit"):
          new_row = pd.DataFrame([{
               "Patient_ID":pid,
               "Date":visit_date.strftime("%Y-%m-%d"),
               "Gender":gender,
               "Hemoglobin":hb,
               "MCH":mch,
               "MCHC":mchc,
               "MCV":mcv,
          }])

          st.session_state.manual_data = pd.concat([st.session_state.manual_data, new_row], ignore_index=True)


          st.success("✅ Visit added. Add more - or switch tabs to analyze.")

     data = st.session_state.manual_data

if data is None or data.empty:
     st.warning("No data to display yet.")
     st.stop()

if data.empty and mode != "Manual Entry":
     st.warning("No data to display yet.")
     st.stop()

filtered_df, has_date, has_patient  = prepare_patient_view(data)

@st.cache_resource
def load_model():
    return joblib.load("model/anemia_model.pkl")

model = load_model()

@st.cache_data
def cached_predictions(df, _model, features):
     return run_predictions(df, _model, features)

@st.cache_data
def cached_pdf(results, patient_id, chart_path):
     return generate_pdf(results, patient_id=patient_id, chart_path=chart_path)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
     "📊 Overview",
     "🧠 Predictions",
     "📈 Trends",
     "🔮 Forecast",
     "💡 Insights"
])

with tab1:
     st.subheader("Dataset Overview")
     st.dataframe(data.head(), use_container_width=True)
     st.info("Use the other tabs to explore predictions risk trends, " 
             "and presonalized guidance.")
     

with tab2:
     st.header("🧠 Anemia Predictions")
     results = cached_predictions(filtered_df, model, REQUIRED_FEATURES)
     results["Recommendation"] = results.apply(lambda r: get_recommendation(r["Risk Probability (%)"], r["Hemoglobin"]), axis=1)

     st.subheader("📋 Patient Risk Table")
     st.dataframe(results.style.applymap(color_risk, subset=["Risk Probability (%)"]), use_container_width=True)

     csv = results.to_csv(index=False).encode("utf-8")
     st.download_button(
          label="⬇️ Download Predictions (CSV)", data=csv, file_name="anemia_prediction.csv", mime="text/csv"
     )

with tab3:
     st.subheader("Risk & Hemoglobin Trends")
     plot_hb_dist(filtered_df)
     if not has_date or len(filtered_df) < 2:
          st.info("Add at least 2 dated records to see trends.")
     else:
          plot_hb_trend(filtered_df, has_date)
          plot_risk_trend(results, filtered_df, has_date)
 

with tab4:
     st.subheader("Risk Forecast (Next Visit)")
     if not has_date or len(filtered_df) < 2:
          st.info("Add at least 2 dated records to see trends.")
     else:
          future_prob, future_preds = forecast_next_visit(results, filtered_df, model)
          fig = plot_forecast(results, filtered_df, future_prob, future_preds, has_date)
          tmp_dir = tempfile.gettempdir()
          chart_path = os.path.join(tmp_dir, "risk_chart.png")
          fig.savefig(chart_path, dpi=150, bbox_inches="tight")
          pdf_buffer = cached_pdf(results, patient_id=filtered_df["Patient_ID"].iloc[0] if has_patient else None, chart_path=chart_path)
          st.download_button(
          label="Download PDF Report", data=pdf_buffer, file_name="anemia_report.pdf", mime="application/pdf"
          )
          st.subheader("🔮 Predicted Next-Visit Risk")
          st.markdown(f"""
                      ### **{future_prob:.1f}%**
                       _Risk estimate based on current trend_
                      """)

with tab5:
     st.subheader("Clinical-style Interpretation")   
     if has_patient:
          st.write(trend_message(filtered_df["Hemoglobin"]))    
     else:
          st.info("Select a patient to view individualized interpretation")       

st.markdown("---")
st.caption("An interactive anemia risk analysis dashboard for educational use.")