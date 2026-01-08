def get_recommendation(prob, hb):
     if prob is None:
          return "Prediction unavialable - backend error."
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
     if val is None:
          return ""
     if val >= 80:
          return "background-color:#d9534f; color:white; font-weight:bold"
     if val >= 50:
          return "background-color:#f0ad4e; color:black; font-weight:bold"
     return "background-color:#5cb85c; color:white; font-weight:bold"
