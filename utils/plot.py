import streamlit as st
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

DATE_COL = "Date"

def plot_hb_dist(df):
    st.subheader("📈 Hemoglobin Distribution")
    fig = px.histogram(df,
                       x="Hemoglobin",
                       nbins=20,
                       opacity=0.75,
                       title="Hemoglobin Distribution",
                       marginal="box")
    fig.update_layout(xaxis_title="Hemoglobin", yaxis_title="Count", height=400)
    st.plotly_chart(fig, use_container_width=True)

def plot_hb_trend(df, has_date):
    st.subheader("Hemoglobin Trend")
    if not has_date:
        st.info("Add Date column to see trends.")
        return

    fig = px.line(df,
                  x="Date",
                  y="Hemoglobin",
                  markers=True,
                  title="Hemoglobin Trend Over Time")
    fig.add_hline(y=12, line_dash="dash", line_color="red", annotation_text="Low Threshold")
    fig.update_xaxes(tickformat="%Y-%m-%d", tickangle=-30, showgrid=True)
    fig.update_yaxes(title="Hemoglobin")
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

def plot_risk_trend(results, df, has_date):
    st.subheader("Risk Trend")
    if not has_date:
        st.info("Add Date column to enable risk monitoring.")
        return
    if len(results) < 2:
        st.info("Not enough data points to show risk trend")
    trend_df = results.groupby("Date",as_index=False)["Risk Probability (%)"].mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trend_df["Date"],
                             y=trend_df["Risk Probability (%)"],
                             mode="lines+markers",
                             name="Historical Risk",
                             line=dict(width=3,color="#4CC9F0"),
                             marker=dict(size=6)
                             ))
    fig.update_layout(
         title="Anemia Risk Trend Over Time",
         xaxis_title="Date",
         yaxis_title="Risk (%)",
         hovermode="x unified",
         template="plotly_dark"
    )
    fig.update_xaxes(tickformat="%Y-%m-%d",tickangle=-30,showgrid=True)
    fig.update_yaxes(showgrid=True, range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)
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
    results = results.sort_values("Date")
    if not has_date or len(results) <= 2:
        st.info("Need atleast 2 dated visits to forecast risk.")
        return
    trend_df = results.groupby("Date",as_index=False)["Risk Probability (%)"].mean()
    last_date = trend_df["Date"].iloc[-1]
    last_risk = trend_df["Risk Probability (%)"].iloc[-1]
    trend = last_risk - trend_df["Risk Probability (%)"].iloc[-2]
    future_prob = max(min(future_prob, last_risk + 15), last_risk - 15)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trend_df["Date"],
                             y=trend_df["Risk Probability (%)"],
                             mode="lines+markers",
                             name="Past Risk",
                             line=dict(color="lightgray",width=3),
                             marker=dict(size=5),
                             opacity=0.5
                             ))


    fig.add_trace(go.Scatter(x=[last_date, future_date],
                             y=[last_risk, future_prob],
                             mode="lines",
                             name="Forecast Path",
                             line=dict(color="orange", width=5, dash="dash")
                             ))
    
    fig.add_trace(go.Scatter(x=[future_date],
                             y=[future_prob],
                             mode="markers",
                             name="Predicted Next Visit",
                             marker=dict(size=16,color="red")
                             ))
    fig.add_vline(x=future_date, line_width=2, line_dash="dot", line_color="red")
    fig.update_xaxes(tickformat="%Y-%m-%d", tickangle=-30, showgrid=True)
    fig.update_yaxes(showgrid=True, range=[0, 100])
    fig.update_layout(title="Anemia Risk Forecast (Next Visit)",
                      xaxis_title="Date",
                      yaxis_title="Risk (%)",
                      legend_title="Legend",
                      template="plotly_dark",
                      hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
    
    if future_prob >= 80 and trend > 5:
          st.error("🔴 High likelihood of anemia worsening - medical review recommended.")
    elif future_prob >= 60 and trend > 2:
          st.warning("🟠 Risk is gradually increasing - monitor closely")
    elif future_prob >= 60:
         st.info("🟡 Moderate but stable risk - no immediate worsening.")
    else:
          st.success("🟢 Risk expected to remain stable or improve")  
    
    return fig