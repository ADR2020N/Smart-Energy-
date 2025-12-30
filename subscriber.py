# -----------------------------------
# Streamlit Smart Energy Dashboard (Dynamic Meter Selection)
# -----------------------------------

import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from datetime import datetime, timedelta

# -----------------------------
# PostgreSQL Configuration
# -----------------------------
DB_HOST = "localhost"
DB_PORT = 5433
DB_NAME = "smart_grid"
DB_USER = "postgres"
DB_PASSWORD = "root"

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

# -----------------------------
# Streamlit Page Configuration
# -----------------------------
st.set_page_config(page_title="Smart Energy Dashboard", layout="wide")
st.title("Smart Energy Consumption Dashboard")

# -----------------------------
# Fetch available meters
# -----------------------------
meter_list = pd.read_sql("SELECT DISTINCT meter_id FROM energy_readings ORDER BY meter_id", conn)
meter_options = meter_list['meter_id'].tolist()

# Default meter is 1000000009
selected_meter = st.sidebar.selectbox("Select Meter ID:", meter_options, index=meter_options.index("1000000009"))

st.markdown(f"Displaying data for meter ID: **{selected_meter}**")

# -----------------------------
# Daily Consumption: Today vs Yesterday
# -----------------------------
st.subheader("Daily Consumption Pattern (Today vs Yesterday)")

query_daily = f"""
SELECT 
    date_trunc('hour', "timestamp") AS bucket,
    AVG(power) AS avg_power
FROM energy_readings
WHERE meter_id = '{selected_meter}'
  AND "timestamp" >= NOW() - INTERVAL '2 day'
GROUP BY bucket
ORDER BY bucket;
"""

df_daily = pd.read_sql(query_daily, conn)

if not df_daily.empty:
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    df_daily['date'] = df_daily['bucket'].dt.date
    df_today = df_daily[df_daily['date'] == today]
    df_yesterday = df_daily[df_daily['date'] == yesterday]

    fig_daily = px.line()
    if not df_yesterday.empty:
        fig_daily.add_scatter(x=df_yesterday['bucket'], y=df_yesterday['avg_power'],
                              mode='lines+markers', name='Yesterday')
    if not df_today.empty:
        fig_daily.add_scatter(x=df_today['bucket'], y=df_today['avg_power'],
                              mode='lines+markers', name='Today')

    fig_daily.update_layout(
        xaxis_title="Hour",
        yaxis_title="Average Power (kW)",
        legend_title="Day"
    )
    st.plotly_chart(fig_daily, use_container_width=True)
else:
    st.info("No data available for this meter.")

# -----------------------------
# Weekly Consumption Overview
# -----------------------------
st.subheader("Weekly Energy Consumption Overview")

query_week = f"""
SELECT 
    date_trunc('day', "timestamp") AS day_bucket,
    SUM(energy) AS total_energy
FROM energy_readings
WHERE meter_id = '{selected_meter}'
  AND "timestamp" >= NOW() - INTERVAL '7 day'
GROUP BY day_bucket
ORDER BY day_bucket;
"""

df_week = pd.read_sql(query_week, conn)

if not df_week.empty:
    fig_week = px.bar(df_week, x='day_bucket', y='total_energy',
                      labels={'day_bucket':'Date','total_energy':'Energy (kWh)'},
                      title=f"Total Energy Consumption Last 7 Days for Meter {selected_meter}")
    st.plotly_chart(fig_week, use_container_width=True)
else:
    st.info("No weekly data available.")

# -----------------------------
# Latest Meter Readings Table
# -----------------------------
st.subheader("Latest Meter Readings")

query_latest = f"""
SELECT * 
FROM energy_readings
WHERE meter_id = '{selected_meter}'
ORDER BY "timestamp" DESC
LIMIT 10;
"""

df_latest = pd.read_sql(query_latest, conn)

if not df_latest.empty:
    st.dataframe(df_latest)
else:
    st.info("No readings available for this meter.")

# -----------------------------
# Close connection on exit
# -----------------------------
conn.close()
