"""
Smart Energy Dashboard
"""

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
from datetime import datetime, timedelta

# -----------------------------
# PostgreSQL connection
# -----------------------------
DB_HOST = "localhost"
DB_PORT = 5433
DB_NAME = "smart_grid"
DB_USER = "postgres"
DB_PASSWORD = "root"

# Create SQLAlchemy engine for use with pandas
DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL)

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Smart Energy Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# CSS Styling: Dark theme & visibility
# -----------------------------
st.markdown("""
<style>
/* Main page background */
body, .block-container {
    background-color: #000000 !important;
    color: #ffffff !important;
}

/* Top banner info */
#top-banner {
    background-color: #111111;
    color: #ffffff;
    padding: 12px 20px;
    font-size: 18px;
    font-weight: bold;
    border-radius: 5px;
    margin-bottom: 15px;
}

/* Sidebar */
.sidebar .sidebar-content {
    background-color: #111111 !important;
    color: #ffffff !important;
}
.stSelectbox > div, .stRadio > div label, .stRadio > div span, .stSelectbox label {
    color: #ffffff !important;
}

/* KPIs */
[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: bold;
    font-size: 32px;
}

/* Metric label styling to improve visibility */
[data-testid="stMetricLabel"] {
    color: #e6e6e6 !important;
    font-weight: 700 !important;
    font-size: 14px !important;
}

/* Metric container for contrast */
.stMetric, .stMetricContainer {
    background-color: #0f0f0f !important;
    padding: 8px 10px !important;
    border-radius: 8px !important;
}

/* Plotly chart background */
[data-testid="stPlotlyChart"] div {
    background-color: #000000 !important;
}

/* Modebar (Plotly toolbar) and small title/icon tweaks */
.js-plotly-plot .modebar, .modebar {
    background: transparent !important;
}
.js-plotly-plot .modebar .modebar-btn, .modebar .modebar-btn {
    background: rgba(255,255,255,0.06) !important;
}
.js-plotly-plot .modebar .modebar-btn svg path, .modebar .modebar-btn svg path {
    stroke: #ffffff !important;
    fill: #ffffff !important;
}
.js-plotly-plot .modebar .modebar-btn, .modebar .modebar-btn {
    color: #ffffff !important;
}
.js-plotly-plot .plotly .main-svg, .plotly .main-svg {
    color: #ffffff !important;
}

/* Table styling */
.stDataFrame div[role="table"] {
    background-color: #111111 !important;
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.title("Select Meter & Time Range")

# Fetch meter IDs dynamically
meter_query = "SELECT DISTINCT meter_id FROM energy_readings ORDER BY meter_id;"
try:
    meter_ids = pd.read_sql(meter_query, engine)['meter_id'].tolist()
except Exception:
    meter_ids = []

if not meter_ids:
    st.error("No meters found in the database. Check DB connection and data.")
    st.stop()

selected_meter = st.sidebar.selectbox("Select Meter ID:", meter_ids)

time_range = st.sidebar.radio(
    "Select Time Range",
    ("Last 1 Hour", "Last 24 Hours", "Last 7 Days")
)

# -----------------------------
# Determine datetime range
# -----------------------------
now = datetime.now()
if time_range == "Last 1 Hour":
    start_time = now - timedelta(hours=1)
elif time_range == "Last 24 Hours":
    start_time = now - timedelta(days=1)
else:
    start_time = now - timedelta(days=7)

# -----------------------------
# Top Banner with dynamic time
# -----------------------------
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(
    f'<div id="top-banner">🔌 Smart Energy Dashboard | Meter ID: {selected_meter} | Time Range: {time_range} | Current Time: {current_time}</div>', 
    unsafe_allow_html=True
)

# -----------------------------
# Fetch Key Metrics
# -----------------------------
metrics_query = f"""
SELECT 
    AVG(power) AS avg_power,
    MAX(power) AS peak_power,
    AVG(voltage) AS avg_voltage,
    AVG(current) AS avg_current,
    AVG(frequency) AS avg_frequency
FROM energy_readings
WHERE meter_id = '{selected_meter}'
AND "timestamp" >= '{start_time}';
"""

metrics = pd.read_sql(metrics_query, engine).iloc[0]

# -----------------------------
# Safe formatting
# -----------------------------
def safe_format(value):
    return f"{value:.2f}" if value is not None else "N/A"

# -----------------------------
# KPIs
# -----------------------------
st.subheader("Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Avg Power (kW)", safe_format(metrics['avg_power']))
col2.metric("Peak Power (kW)", safe_format(metrics['peak_power']))
col3.metric("Avg Voltage (V)", safe_format(metrics['avg_voltage']))
col4.metric("Avg Current (A)", safe_format(metrics['avg_current']))
col5.metric("Avg Frequency (Hz)", safe_format(metrics['avg_frequency']))

# -----------------------------
# Aggregated Data for Charts
# -----------------------------
chart_query = f"""
SELECT date_trunc('hour', "timestamp") AS bucket,
       AVG(power) AS avg_power,
       AVG(voltage) AS avg_voltage,
       AVG(current) AS avg_current,
       AVG(frequency) AS avg_frequency
FROM energy_readings
WHERE meter_id = '{selected_meter}'
AND "timestamp" >= '{start_time}'
GROUP BY bucket
ORDER BY bucket;
"""
df_chart = pd.read_sql(chart_query, engine)

# -----------------------------
# Energy Trends Charts
# -----------------------------
st.subheader(f"Energy Trends ({time_range})")

# Two charts per row
col1, col2 = st.columns(2)
fig_power = px.line(df_chart, x='bucket', y='avg_power', title="Power Trend (kW)", template="plotly_dark")
fig_voltage = px.line(df_chart, x='bucket', y='avg_voltage', title="Voltage Trend (V)", template="plotly_dark")
col1.plotly_chart(fig_power, width='stretch')
col2.plotly_chart(fig_voltage, width='stretch')

col3, col4 = st.columns(2)
fig_current = px.line(df_chart, x='bucket', y='avg_current', title="Current Trend (A)", template="plotly_dark")
fig_frequency = px.line(df_chart, x='bucket', y='avg_frequency', title="Frequency Trend (Hz)", template="plotly_dark")
col3.plotly_chart(fig_current, width='stretch')
col4.plotly_chart(fig_frequency, width='stretch')

# -----------------------------
# Real-Time Table (At the Bottom)
# -----------------------------
st.subheader(f"Real-Time Meter Readings ({time_range})")
realtime_query = f"""
SELECT * FROM energy_readings
WHERE meter_id = '{selected_meter}'
AND "timestamp" >= '{start_time}'
ORDER BY "timestamp" DESC
LIMIT 50;
"""
df_realtime = pd.read_sql(realtime_query, engine)

if df_realtime.empty:
    st.info(f"No data for the selected time range ({time_range}).")
else:
    st.dataframe(df_realtime)
