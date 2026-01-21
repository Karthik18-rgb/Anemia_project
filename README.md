# 🩸 Anemia Risk Detection & Forecasting System
 An end-to-end Machine Learning application to detect anemia risk from blood parameters, monitor risk trends over time, and forecast next-visit risk using calibrated probabilistic models. 
 Built using **Python, Scikit-learn, FastAPI, Streamlit, Plotly**, and real-world ML pipelines. 
---
  ## 🚀 Features 
  - ✅ Predict anemia risk probability from blood test values 
  - 📊 Interactive risk & hemoglobin trend visualization 
  - 🔮 Forecast next-visit anemia risk using ML + trend modeling 
  - 🧠 Calibrated probabilistic ML model (Logistic Regression pipeline) 
  - 🌐 Backend REST API using FastAPI 
  - 🖥️ Frontend dashboard using Streamlit + Plotly 
  - 📄 PDF medical-style report generation 
  - 🧪 Demo mode, CSV upload & manual patient entry support
---
## 🏗️ System Architecture 
User → Streamlit Dashboard → FastAPI Backend → ML Model ↓ Plotly Visualizations ↓ PDF Report Export
--- 
## 📁 Project Structure 
anemia_project/ 
│ 
├── app.py # Streamlit frontend 
├── train_model.py # Model training pipeline 
├── model/ 
│ └── anemia_model.pkl # Trained ML pipeline 
│ 
├── utils/
│ 
├── preprocessing.py # Data cleaning & filtering 
│ ├── prediction.py # API calls + forecasting logic 
│ ├── plot.py # Interactive visualizations 
│ ├── risk.py # Risk interpretation logic 
│ └── pdf_export.py # PDF report generation 
├── backend/ 
| ├── main.py # FastAPI app  
| ├── services.py # Model inference services 
| ├── schemas.py # Pydantic schemas  
| ├── models.py # ORM / DB models (optional) 
| ├── database.py # DB connection logic
| └── crud.py # DB operations
│ 
├── data/ 
  ├── raw/
    └── anemia.csv  
│ └── sample.csv 
│ 
├── requirements.txt 
└── README.md
--- 
## 🧠 Machine Learning Details
 ### Input Features 
 - Gender
 - Hemoglobin 
 - MCH 
 - MCHC 
 - MCV 
 --- 
 ### Model Architecture
  The system uses a production-grade **Logistic Regression pipeline**:
   ```python Pipeline([ ("impute", SimpleImputer(strategy="median")), ("scaler", StandardScaler()), ("model", LogisticRegression(class_weight="balanced", max_iter=1000)) ]) 

Components:
- SimpleImputer (median) – handles missing values

StandardScaler – normalizes feature ranges

Logistic Regression – outputs stable probabilities

Class weighting – handles dataset imbalance

Why Logistic Regression?

Produces reliable probability estimates

Naturally interpretable for medical risk analysis

Less prone to overconfidence than tree models

Works well on small & imbalanced clinical datasets

Stable for deployment and forecasting

Probability Calibration

Using standardized features + class-balanced logistic regression ensures:

No probability saturation (0% / 100%)

Smooth risk transitions

Clinically meaningful outputs

📊 Forecasting Logic

Next-visit forecasting uses:

Current predicted risk

Hemoglobin trend over last 3 visits

Trend-to-risk transformation

Bounded projection (5% – 95%)

Time extrapolation (30 days)

This avoids unrealistic probability jumps and prevents ML misuse for time forecasting.

⚙️ Installation

git clone <repo-url> cd anemia_project python -m venv venv source venv/bin/activate # Linux / macOS venv\Scripts\activate # Windows pip install -r requirements.txt 

▶️ Run Backend (FastAPI)

cd backend uvicorn main:app --reload 

▶️ Run Frontend (Streamlit)

streamlit run app.py 

🧪 Demo Credentials

Username: doctor 
Password: anemia123 

Recommended:

Overview tab

Prediction table

Trend plots

Forecast screen

PDF export

🧩 Challenges Solved

Probability saturation (99–100% outputs)

Patient ID datetime conversion bug (1970 epoch issue)

Sorting instability

Backend ↔ frontend prediction mismatch

Feature scaling errors

Forecast logic misuse

Rolling probability smoothing bugs

Plotly axis formatting

PDF export consistency

🔮 Future Improvements

True next-visit ML forecasting model (sequence-based)

Multi-patient temporal modeling

Confidence intervals

SHAP explainability

Doctor role authentication

PostgreSQL integration

Cloud deployment (Docker + CI/CD)

Mobile responsive UI

⚠️ Medical Disclaimer

This system is intended for educational and research purposes only.
It does not replace professional medical diagnosis or treatment.
Always consult a qualified healthcare provider for clinical decisions.

🧑‍💻 Author

Karthik Singh
B.Tech Student | ML & Data Engineering Enthusiast
Built after hours of debugging, broken graphs, broken models, probability explosions, and persistence.
If you found this useful ⭐ the repo.
