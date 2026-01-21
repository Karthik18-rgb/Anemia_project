import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (classification_report,
                             confusion_matrix,
                             precision_score,
                             recall_score,
                             f1_score)
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
import joblib


df = pd.read_csv("data/raw/anemia.csv")

X = df[["Gender", "Hemoglobin", "MCH", "MCHC", "MCV"]]
y = df["Result"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

pipe = Pipeline([("impute", SimpleImputer(strategy='median')),
                 ("scaler", StandardScaler()),
                 ("model", LogisticRegression(max_iter=1000,class_weight='balanced'))])

pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)

print("\nConfusion Matrix\n", confusion_matrix(y_test, y_pred))

precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"\nPrecision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score:{f1:.4f}")

print("\nDetailed Breakdown:\n")
print(classification_report(y_test, y_pred))


joblib.dump(pipe,"model/anemia_model.pkl")
print("Saved Logistic Regression Model")

