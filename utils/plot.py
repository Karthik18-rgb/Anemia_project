import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

DATE_COL = "Date"

def plot_hb_dist(df):
    st.subheader("📈 Hemoglobin Distribution")
    fig, ax = plt.subplots(figsize=(10,5))
    sns.histplot(df["Hemoglobin"], kde=True, ax=ax)
    ax.set_xlabel("Hemoglobin")
    st.pyplot(fig)

def plot_hb_trend(df, has_date):
    st.subheader("Hemoglobin Trend")
    if not has_date:
        st.info("Add Date column to see trends.")
        return

    fig, ax = plt.subplots(figsize=(10,5))
    sns.lineplot(x=df[DATE_COL], y=df["Hemoglobin"], marker='o',ax=ax)
    ax.axhline(12,label="Low Threshold", color="red", linestyle="--")
    ax.set_ylabel("Hemoglobin")
    ax.legend()
    plt.xticks(rotation=30)
    fig.autofmt_xdate()
    st.pyplot(fig)

def plot_risk_trend(results, df, has_date):
    st.subheader("Risk Trend")
    if not has_date:
        st.info("Add Date column to enable risk monitoring.")
        return
    fig, ax = plt.subplots(figsize=(10,5))
    sns.lineplot(x=results[DATE_COL], y=results["Risk Probability (%)"], marker='o', ax=ax, color="#1f77b4")
    ax.set_ylabel("Risk (%)")
    ax.set_title("Historical Anemia Risk Trend")
    plt.xticks(rotation=30)
    fig.autofmt_xdate()
    st.pyplot(fig)

    risk_series = results["Risk Probability (%)"].dropna()
    if len(risk_series) > 1:
         slope = risk_series.diff().mean()
    else:
         slope = 0
             
    if slope > 5:
          st.error("🚨 Risk is increasing rapidly - medical review recommended.")
    elif slope > 0:
          st.warning("📈 Risk is slowly increasing - keep monitoring")
    else:
          st.success("🟢 Risk appears stable or improving")  

def plot_forecast(results, df, future_prob, future_date, has_date):
    if not has_date or len(results) <= 2:
        st.info("Need atleast 2 dated visits to forecast risk.")
        return
    fig, ax = plt.subplots(figsize=(10,5))
    ax.plot(df["Date"],results["Risk Probability (%)"], marker='o',color="grey", label="Historical Risk")
    ax.plot(future_date, future_prob, "ro",markersize=10, label="Predicted Next Visit")
    ax.plot([df["Date"].iloc[-1], future_date], [results["Risk Probability (%)"].iloc[-1], future_prob],
            "r--", alpha=0.7)
    ax.set_ylabel("Risk (%)")
    ax.set_title("Anemia Risk Forecast")
    plt.xticks(rotation=30)
    fig.autofmt_xdate()
    st.pyplot(fig)
    
    if future_prob >= 80:
          st.error("🔴 High likelihood of anemia worsening - medical review recommended.")
    elif future_prob >= 60:
          st.warning("🟠 Risk is gradually increasing - monitor closely")
    else:
          st.success("🟢 Risk expected to remain stable or improve")  
    
    return fig